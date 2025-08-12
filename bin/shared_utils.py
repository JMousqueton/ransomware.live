import os, json, hashlib,re, html
import asyncio
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFilter
from PIL.PngImagePlugin import PngInfo
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
## Hudsonrock 
import tldextract
import hudsonrockapi
import httpx
import shared_utils
##Enrichment
from typing import Any, Dict, List, Union

import shutil
import logging
#IA DETECTION 
import cv2

#Appender
from openai import OpenAI
#from mistralai import Mistral
import pycountry

from playwright.async_api import async_playwright

# mail 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

# Notif
import http.client, urllib
import requests
import base64

### screenshot 
from libcapture import capture_victim

# Load environment variables from ../.env
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
# Paths from environment variables
home = os.getenv("RANSOMWARELIVE_HOME")
db_dir = Path(home + os.getenv("DB_DIR"))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
proxy_address = os.getenv("TOR_PROXY_SERVER", "socks5://127.0.0.1:9050")  # Default to Tor proxy


logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
)

def stdlog(msg):
    logging.info(msg)

def errlog(msg):
    logging.error(msg)

# Load the pre-trained Haar Cascade classifier for face detection 
face_cascade = cv2.CascadeClassifier('/opt/ransomwarelive/etc/haarcascade_frontalface_default.xml')

def check_image_for_face(image_path, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)):
    """
    Checks if an image contains a detectable face using a Haar Cascade Classifier.

    :param image_path: Path to the image file.
    :param scaleFactor: How much the image size is reduced at each image scale.
    :param minNeighbors: Minimum number of neighbors a rectangle should have to be retained.
    :param minSize: Minimum size of detected objects (width, height).
    :return: Tuple (bool, str). True if a face is detected, False otherwise. Second value contains an error message or success status.
    """
    try:
        # Attempt to load the image
        image_path = str(image_path)
        image = cv2.imread(image_path)

        if image is None:
            return False, f"Error loading image {image_path}. Check if the file exists and is a valid image."

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect objects in the image (using face detection as an example)
        objects = face_cascade.detectMultiScale(gray_image, scaleFactor=scaleFactor, minNeighbors=minNeighbors, minSize=minSize)

        # Check if any objects were detected
        if len(objects) > 0:
            stdlog(f"OpenCV: {len(objects)} face(s) detected.")
            return True
        else:
            stdlog( "OpenCV: No faces detected.")
            return False
    except cv2.error as e:
        errlog(f"OpenCV: error: {str(e)}")
        return False
    except Exception as e:
        errlog( f"OpenCV: An error occurred: {str(e)}")
        return False

def enrich_post(title: str, description: str) -> Dict[str, Any]:
    OPENAPI_MODEL = "gpt-4o-mini"
    OPENAPI_TEMPERATURE = 0.0
    PROMPT_TEMPLATE = (
    "You are a threat intelligence assistant and tracking posts of ransomware groups. They only display alleged victim names on their leak sites.\n"
    "The victim name is: '{title}' and the post description is: {description}\n\n"
    "I need you to help me find the following information about the victim"
    "and answer in strict JSON with these keys ONLY:\n"
    "  company_name   (string)\n"
    "  country        (string, ISO 3166‑1 country name if known, else \"unknown\")\n"
    "  sector         (list, the list of sectors the victim belongs to. Use sectors from the NIS Directive\n"
    "  url            (string, victim's official website or \"unknown\")\n"
    "  summary        (string, ≤ 50 words)\n\n"
    "If you are uncertain about a field, put \"unknown\", but do not invent facts.\n"
    "For the country location, use the company address as displayed by the Google search.\n"    
    )
    prompt = PROMPT_TEMPLATE.format(title=title, description=description)
    openai.api_key = OPENAI_API_KEY
    response = openai.chat.completions.create(
        model=OPENAPI_MODEL,
        temperature=OPENAPI_TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a threat intelligence assistant supporting a CTI team tracking ransomware incidents."},
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)




def openjson(file):
    '''
    opens a file and returns the json as a dict
    '''
    with open(file, encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    return data

def isexception(victim, group):
    try:
        with open('exceptions.lst', 'r') as file:
            for line in file:
                line_victim, line_group = line.strip().split(';')
                if line_victim == victim and line_group == group:
                    return True
        return False
    except FileNotFoundError:
        errlog("The file 'exceptions.lst' was not found.")
        return False

def extract_fqdn(url):
    # Extract components using tldextract
    extract_result = tldextract.extract(url)
    
    # Exclude 'www' if it is the subdomain
    subdomain = '' if extract_result.subdomain == 'www' else extract_result.subdomain
    
    # Combine the extracted parts to form the FQDN
    fqdn = '.'.join(part for part in [subdomain, extract_result.domain, extract_result.suffix] if part)
    return fqdn

# Function to get the current timestamp in the desired format
def get_current_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

def is_file_older_than(filepath, duration_minutes):
    """
    Checks if a file is older than a specified duration in minutes.

    Args:
        filepath (Path): Path to the file to check.
        duration_minutes (int): Duration in minutes to compare the file's age against.

    Returns:
        bool: True if the file is older than the specified duration or does not exist, False otherwise.
    """
    filepath = Path(filepath)
    if filepath.exists():
        file_age = datetime.utcnow() - datetime.fromtimestamp(filepath.stat().st_mtime)
        return file_age > timedelta(minutes=duration_minutes)
    return True  # Treat non-existent files as "old"

def url_to_md5(url):
    return hashlib.md5(url.encode("utf-8")).hexdigest() 

async def take_screenshot_victim(url):
    TOR_PROXY = "socks5://127.0.0.1:9050"
    OUTPUT_DIR = "/opt/ransomwarelive/images/victims"
    WATERMARK_PATH = Path("/opt/ransomwarelive/images/ransomwarelive.png")
    md5_base = url_to_md5(url)
    segment_dir = os.path.join(OUTPUT_DIR, f"{md5_base}_segments")
    final_path = None
    os.makedirs(segment_dir, exist_ok=True)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(proxy={"server": TOR_PROXY}, headless=True)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()

            print(f"[+] Navigating to {url} via Tor...")
            await page.goto(url, timeout=60000)

            print("[~] Waiting for page to fully render...")
            await asyncio.sleep(20)

            print("[~] Detecting largest scrollable element...")
            scrollable_selector = await page.evaluate("""
                () => {
                    function getScrollableElements() {
                        return Array.from(document.querySelectorAll('*')).filter(el => {
                            const style = window.getComputedStyle(el);
                            return (
                                (style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                                el.scrollHeight > el.clientHeight
                            );
                        });
                    }

                    const scrollables = getScrollableElements();
                    if (scrollables.length === 0) return null;

                    let maxEl = scrollables[0];
                    for (const el of scrollables) {
                        if (el.scrollHeight > maxEl.scrollHeight) {
                            maxEl = el;
                        }
                    }

                    maxEl.setAttribute("data-scroll-target", "true");
                    return "[data-scroll-target='true']";
                }
            """)

            if not scrollable_selector:
                print("[!] No scrollable container found. Falling back to full page screenshot.")
                final_path = os.path.join(OUTPUT_DIR, md5_base + ".png")
                await page.screenshot(path=final_path, full_page=True)
                print(f"[✓] Full page screenshot saved: {final_path}")
                return

            scroll_height = await page.evaluate(f"""
                () => {{
                    const el = document.querySelector("{scrollable_selector}");
                    return el ? el.scrollHeight : 0;
                }}
            """)

            print(f"[i] Scrollable content height: {scroll_height}px")

            viewport_height = 1000
            await page.set_viewport_size({"width": 1280, "height": viewport_height})

            n = 0
            for y in range(0, scroll_height, viewport_height):
                await page.evaluate(f"""
                    () => {{
                        const el = document.querySelector("{scrollable_selector}");
                        if (el) el.scrollTo(0, {y});
                    }}
                """)
                await asyncio.sleep(1.5)
                segment_path = os.path.join(segment_dir, f"{n:03d}.png")
                scroll_area = await page.query_selector(scrollable_selector)
                await scroll_area.screenshot(path=segment_path)
                print(f"[✓] Captured segment {n} at scroll {y}px")
                n += 1

            images = [Image.open(os.path.join(segment_dir, f)) for f in sorted(os.listdir(segment_dir))]
            total_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)

            stitched = Image.new("RGB", (total_width, total_height))
            offset = 0
            for img in images:
                stitched.paste(img, (0, offset))
                offset += img.height

            final_path = os.path.join(OUTPUT_DIR, md5_base + ".png")
            stitched.save(final_path)
            print(f"[✓] Final stitched screenshot saved: {final_path}")

        except Exception as e:
            print(f"[!] Error: {e}")

        finally:
            await browser.close()
            if final_path and os.path.exists(final_path):
                shared_utils.add_watermark(final_path, WATERMARK_PATH)

            if os.path.exists(segment_dir):
                shutil.rmtree(segment_dir, ignore_errors=True)
                print(f"[🧹] Cleaned up temporary folder: {segment_dir}")




# Function to take a screenshot
async def screenshot(page, image_path, watermark_image_path):
    """
    Takes a screenshot of the given page, applies a watermark, and adds metadata.

    Args:
        page (playwright.async_api.Page): The Playwright page object.
        image_path (Path): Path to save the screenshot.
        watermark_image_path (Path): Path to the watermark image.

    Returns:
        None
    """
    # Take and save the screenshot
    image_path = Path(image_path)
    try:
        # Force page load
        #await page.wait_for_load_state("networkidle")
        #await page.wait_for_timeout(2000)

        await page.screenshot(path=str(image_path), full_page=True,timeout=60000)
        stdlog(f"Screenshot saved at {image_path}")
        if check_image_for_face(image_path):
            body="A new screenshot must be analysed : \n\n https://images.ransomware.live/victims/"+os.path.basename(image_path)
            send_email("[Action Required] Check this screenshot for any ID",body, "support@ransomware.live")
        # Apply watermark
        add_watermark(image_path, watermark_image_path)
        # Add metadata
        add_metadata(image_path)
    except:
        try:
            await page.screenshot(path=str(image_path), timeout=60000)
            stdlog(f"Screenshot saved at {image_path}")
            if check_image_for_face(image_path):
                body="A new screenshot must be analysed : \n\n https://images.ransomware.live/victims/"+os.path.basename(image_path)
                send_email("[Action Required] Check this screenshot for any ID",body, " support@ransomware.live")
            # Apply watermark
            add_watermark(image_path, watermark_image_path)
            # Add metadata
            add_metadata(image_path)
        except Exception as e:
            errlog('Failled to save screenshot: '+ str(e) )

def add_watermark(image_path, watermark_image_path):
    """
    Adds a watermark image to the center of the input image.

    Args:
        image_path (Path): Path to the image to watermark.
        watermark_image_path (Path): Path to the watermark image.

    Returns:
        None
    """
    image_path = Path(image_path)
    watermark_image_path = Path(watermark_image_path)

    original = Image.open(image_path).convert('RGBA')
    watermark = Image.open(watermark_image_path).convert('RGBA')

    # Adjust opacity of watermark
    transparent = Image.new('RGBA', watermark.size, (255, 255, 255, 0))
    for x in range(watermark.width):
        for y in range(watermark.height):
            r, g, b, a = watermark.getpixel((x, y))
            transparent.putpixel((x, y), (r, g, b, int(a * 0.2)))
    watermark = transparent

    # Position watermark in the center
    x = (original.width - watermark.width) // 2
    y = (original.height - watermark.height) // 2
    original.paste(watermark, (x, y), watermark)

    stdlog(f"Watermark added to {image_path}")
    original.save(image_path, 'PNG')

def add_metadata(image_path):
    """
    Adds metadata to the given PNG image.

    Args:
        image_path (Path): Path to the image to add metadata.

    Returns:
        None
    """
    image_path = Path(image_path)
    image = Image.open(image_path)
    metadata = PngInfo()
    metadata.add_text("Source", "Ransomware.live")
    metadata.add_text("Copyright", "Ransomware.live")
    metadata.add_text("Author", "Julien Mousqueton")
    current_date = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
    metadata.add_text("Creation Time", current_date)

    # Optional: Add a timestamp overlay on the image
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), current_date, fill=(0, 0, 0))

    stdlog(f"Metadata added to {image_path}")
    image.save(image_path, pnginfo=metadata)

def send_email(subject, body, to_email, attachment_path=None):
    # Set up the SMTP server
    smtp_server = 'localhost'
    smtp_port = 25
    smtp_tls =  False
    smtp_username = ''
    smtp_password = ''

    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = "noreply@ransomware.live"
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach the image if specified
    if attachment_path:
        attachment = open(attachment_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path)
        msg.attach(part)

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    if smtp_tls:
        server.starttls()
        server.login(smtp_username, smtp_password)

    # Send the email
    server.sendmail(smtp_username, to_email, msg.as_string())

    # Quit the server
    server.quit()
    stdlog('Mail sent')

def clean_slug(url):
    # Remove http://, https://, and trailing slashes
    try:
        cleaned_url = re.sub(r'^https?://|/$', '', url)
        return cleaned_url
    except:
        return url

async def victim_screenshot(post_url, group_name, victim):
    """
    Handles the Playwright browser and calls the screenshot function.

    Args:
        post_url (str): The URL of the post to screenshot.
        group_name (str): Name of the ransomware group.
        victim (str): Name of the victim.

    Returns:
        None
    """
    hash_object = hashlib.md5(post_url.encode('utf-8'))
    hex_digest = hash_object.hexdigest()
    screenshot_path = os.path.join('/opt/ransomwarelive/images/victims', f'{hex_digest}.png')
            
    proxy = "socks5://127.0.0.1:9050"  # Default to Tor's SOCKS proxy
    watermark_path = Path('/opt/ransomwarelive/images/ransomwarelive.png')  # Example watermark path

    async with async_playwright() as playwright:
        '''
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(proxy={"server": proxy})
        '''
        browser = await playwright.chromium.launch(
        #browser = await p.firefox.launch(
            proxy={"server": proxy},
            headless=True
        )
        context = await browser.new_context(ignore_https_errors=True)

        page = await context.new_page()
        
        try:
            stdlog(f"Screenshot {post_url}")
            await page.goto(post_url, timeout=60000)  # Adjust timeout for .onion sites
            await page.mouse.move(x=500, y=400)
            await page.mouse.wheel(delta_y=2000, delta_x=0)
            await page.wait_for_timeout(60000)
            await screenshot(page, screenshot_path, watermark_path)
        except Exception as e:
            errlog(f"Failed to capture screenshot for {post_url}: {e}")
        finally:
            await browser.close()

def get_country(victim,description='',website=''):
    country_names = [
        "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", 
        "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", 
        "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", 
        "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", 
        "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", 
        "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", 
        "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", 
        "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", 
        "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", 
        "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", 
        "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", 
        "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", 
        "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", 
        "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", 
        "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", 
        "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", 
        "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", 
        "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", 
        "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", 
        "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", 
        "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", 
        "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ]


    # Method 1: Analyzing description field for country names

    result = ''
    country_name = ''
    if description == None:
        description = ''
    if description.startswith("Country:"):
        country_name = description.replace("Country:", "").strip()
    elif description.startswith("Country : "):
        country_name = description.split('-')[0].strip().replace("Country : ","")

    if description and not country_name:
        for name_country in country_names:
            if name_country in description:
                country_name = name_country

    if country_name:
        try:
            country_code = pycountry.countries.lookup(country_name).alpha_2
            if country_code != 'EU':
                result = country_code
                #stdlog('Methode 1 : ' + victim + ' ---> ' +  result)
        except LookupError:
            pass
    tld_country_mapping = {
        'com': '',  'org': '',  'net': '',  'gov': 'US',  'edu': 'US',  'int': '',  'mil': 'US',  'biz': '',  'info': '',  
        'name': '',  'eu': '',  'us': 'US',  'uk': 'GB',  'ca': 'CA',  'au': 'AU',  'de': 'DE',  'fr': 'FR',  'it': 'IT',  
        'es': 'ES',  'jp': 'JP',  'cn': 'CN',  'in': 'IN',  'ru': 'RU',  'br': 'BR',  'mx': 'MX',  'nl': 'NL',  'se': 'SE',  
        'no': 'NO',  'fi': 'FI',  'dk': 'DK',  'sg': 'SG',  'za': 'ZA',  'nz': 'NZ',  'ch': 'CH',  'at': 'AT',  'be': 'BE',  
        'pt': 'PT',  'pl': 'PL',  'ie': 'IE',  'gr': 'GR',  'cz': 'CZ',  'hu': 'HU',  'ro': 'RO',  'tr': 'TR',  'kr': 'KR',  
        'il': 'IL',  'ae': 'AE',  'sa': 'SA',  'th': 'TH',  'id': 'ID',  'my': 'MY',  'vn': 'VN',  'ph': 'PH',  'cl': 'CL',  
        'co': 'CO',  'ar': 'AR',  'pe': 'PE',  've': 'VE',  'ng': 'NG',  'eg': 'EG',  'za': 'ZA',  'ke': 'KE',  'ma': 'MA',  
        'tn': 'TN',  'gh': 'GH',  'dz': 'DZ',  'ug': 'UG',  'cm': 'CM',  'sn': 'SN',  'zm': 'ZM',  'bw': 'BW',  'zw': 'ZW',  
        'mw': 'MW',  'mu': 'MU',  'na': 'NA',  'rw': 'RW',  'tz': 'TZ',  'et': 'ET',  'ci': 'CI',  'gm': 'GM',  'lr': 'LR',  
        'mg': 'MG',  'mw': 'MW',  'so': 'SO',  'sd': 'SD',  'tg': 'TG',  'ug': 'UG',  'za': 'ZA',  'ao': 'AO',  'cg': 'CG',  
        'cd': 'CD',  'gh': 'GH',  'ke': 'KE',  'mg': 'MG',  'mu': 'MU',  'mw': 'MW',  'mz': 'MZ',  'na': 'NA',  'rw': 'RW',  
        'sc': 'SC',  'sl': 'SL',  'ug': 'UG',  'zm': 'ZM',  'zw': 'ZW',  'rs': 'RS',  'do': 'DO'
    }

    domain_name_pattern = r"^([a-zA-Z0-9-]+(?:\.[a-zA-Z]+)+)$"

    # Analyzing website field
    if website:
        website = website.replace('https://','').replace('http://','').replace('/','')
        if re.match(domain_name_pattern, website):
            domain_info = website.split('.')[-1] 
            if domain_info.lower() in tld_country_mapping:
                country_code = tld_country_mapping[domain_info.lower()]
                if country_code:
                    result = country_code.upper() 
                    #stdlog('Methode 2 : ' + website + ' --> ' + result)
    return result

def extract_md5_from_filename(file_name):
    parts = file_name.rsplit("-", 1)

    if len(parts) == 2:
        before_hyphen, after_hyphen = parts
        dot_position = after_hyphen.rfind(".")

        if dot_position != -1:
            extracted_text = after_hyphen[:dot_position]
            return extracted_text

def find_slug_by_md5(group_name, target_md5):
    # Load the JSON data from the file or source
    json_file_path = db_dir / "groups.json"
    with json_file_path.open('r') as file:
            data = json.load(file)

    # Find the group entry in the data
    group_entry = next((group for group in data if group['name'] == group_name), None)

    if group_entry:
        # Extract the slugs from the locations
        slugs = [location['slug'] for location in group_entry['locations']]

        # Calculate the MD5 hash for each slug and compare with the target MD5
        for slug in slugs:
            md5 = hashlib.md5(slug.encode()).hexdigest()
            if md5 == target_md5:
                return slug
    else:
        return None

def posttemplate(victim, group_name, timestamp,description,website,published,post_url,country,activity,dup,extra_infos):
    schema = {
        'post_title': victim,
        'group_name': group_name,
        'discovered': timestamp,
        'description': description,
        'website': website,
        'published' : published,
        'post_url' : post_url,
        'country'   : country,
        'activity'  : activity,
        'duplicates' : dup,
        'extrainfos': extra_infos
    }
    return schema


def clean_title(s):
    """
    Cleans the input string by removing unwanted substrings and formatting it.

    Args:
        s (str): The input string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    # Define a list of substrings to remove
    substrings_to_remove = [
        '[DISCLOSED]', '(Updated)', '(updated)','<Auction>', '| Data security breach!', '| Update!', '(SOLD)', '[TORRENT]', '<SOLD>', '<Disclose>', ' leakage', ' LEAKED', ' admin access', ' access admin', ' ()', 'by Babuk Locker 2.0', 'By Babuk Locker 2.0',
        ', Updated data leak.', 'updated','Updated', 'update', '<disclose>', ' - Press Release', ' proof', ' / Database', ' warn', ' by ( Babuk Locker )', ' | SOLD','[EVIDENCE]', 'By ( Babuk Locker )',
        '<', '>', 'Full Data Leak', 'Data Leak', 'pt.2', 'In the depths of software development. Unlocking the secrets of ', '(Part 1)', '(Part 2)', '(Part 3)', '[EVIDANCE] ', '(negotiation started)'
    ]
    
    # Remove defined substrings
    for substring in substrings_to_remove:
        s = s.replace(substring, '')

    # Remove " PoC" if it appears at the end of the string
    s = re.sub(r' PoC$', '', s)
    
    # Replace multiple spaces with a single space
    s = re.sub(r' +', ' ', s)
    
    # Trim leading and trailing spaces
    s = s.strip()
    
    return s

def existingpost(post_title, group_name):
    """
    Check if a post already exists in victims.json.
    """
    json_file_path = db_dir / "victims.json"
    normalized_title = post_title.lower()
    variants = {
        normalized_title,
        'www.' + normalized_title,
        normalized_title.replace('www.', '')
    }

    with json_file_path.open('r') as file:
        posts = json.load(file)
        for post in posts:
            if post['group_name'] == group_name and post['post_title'].lower() in variants:
                return True
    return False


def appender(victim,group_name,description='',website='', published='', post_url='',country='',extra_infos=[]):
    with open(db_dir / 'victims.json', encoding='utf-8') as jsonfile:
        posts = json.load(jsonfile)
    if len(victim) == 0:
        errlog('Victim is empty')
        return
    if len(victim) > 90:
        victim = victim[:90] + '...'
    victim = html.unescape(victim)
    victim = clean_title(victim)
    if os.path.exists("exceptions.lst") and isexception(victim, group_name):
        # stdlog('Exception found for ' + victim)
        return
    if existingpost(victim, group_name) is True:
        return
   
    stdlog(f'[{group_name}] Processing ... victim: {victim} - website: {website}')
    # Check if the victim contains an FQDN in parentheses
    fqdn_match = re.search(r'\(([\w.-]+\.[a-zA-Z]{2,})\)', victim)
    if fqdn_match:
        extracted_fqdn = fqdn_match.group(1)
        if not website and ".local" not in extracted_fqdn.lower():  # Only set if website is empty
            website = extracted_fqdn
    # Check if the victim itself is a valid FQDN
    elif not website and re.match(r'^[\w.-]+\.[a-zA-Z]{2,}$', victim):
        website = victim
    if website and len(website) > 6:
            stdlog('Query Hudsonrock with ' + extract_fqdn(website))
            asyncio.run(hudsonrockapi.run_query(extract_fqdn(website)))
    if published:
        try:
            published_date = datetime.fromisoformat(published)
            if published_date > datetime.now():
                published = str(datetime.now())
        except ValueError:
            errlog('Invalid published date format')
            published = str(datetime.today())
    else:
        published = str(datetime.today())
    if post_url:
        #asyncio.run(victim_screenshot(post_url, group_name, victim))
        #asyncio.run(take_screenshot_victim(post_url))
        capture_victim(post_url)
    
    stdlog(f"Querying OpenAI API for '{victim}' activity...")
    # Initialize OpenAI Client
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )   

    # List of known industry sectors
    SECTOR_LIST = [
        "Manufacturing", "Construction", "Transportation/Logistics", "Technology",
        "Healthcare", "Financial Services", "Public Sector", "Education",
        "Business Services", "Consumer Services", "Energy", "Telecommunication",
        "Agriculture and Food Production", "Hospitality and Tourism"
    ]
    prompt = (
        f'Using this list: {", ".join(SECTOR_LIST)}, '
        f'can you determine the sector of this company: "{victim}"? '
        f'Just answer with one word from the list. If you cannot pick one, answer "Not Found".'
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        activity = completion.choices[0].message.content.strip()
        if activity != "Not Found":
            if activity not in SECTOR_LIST:
                activity = "Not Found"
    except Exception as e:
        print(f"⚠️ OpenAI API error: {e}")
        activity =  "Not Found"

    ## Get Website 
    if OPENAI_API_KEY and website is None and description:
        client = OpenAI()
        stdlog(f'Query OpenAI API for "{victim}" website')
        prompt = f'can you give me your best guess for the domain name of "{victim}" Only give me the domain name, no extract text. if you cannot guess just answer "Not Found"'
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        website = completion.choices[0].message.content
        if website == "Not Found":
            website = ''

    if website == None:
        website = ''

    ### Get Country 
    #country = get_country(victim,description,website)
    if OPENAI_API_KEY and (country is None or len(country) < 2) and '*' not in victim:
        stdlog(f'Query OpenAI API for "{victim}" country')
        client = OpenAI()
        prompt = f'I would like the 2 letters code of the country, and only the 2 letters not extra text, where the this company is located : "{victim}"'
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        country = completion.choices[0].message.content
        stdlog(f'Found : {country}')
    
    if len(country) == 2:
        try:
            pycountry.countries.get(alpha_2=country.upper())
        except:
            country = ''
    else:
        country = ''
        
 
    ### Get Description 
    if OPENAI_API_KEY and description == '' and '*' not in victim:
        stdlog(f'Query OpenAI API for "{victim}" description')
        client = OpenAI()
        prompt = f'Can you provide a detailed description for the company "{victim}" in around 400 chars and without any links ? If you cannot just answer "N/A".'
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        description = completion.choices[0].message.content
        description = '[AI generated] ' + description

    now = str(datetime.today())
    if not published:
        published = now


    victim_domain = get_domain(website)
    #print('* ' + website + ' ---> ' + victim_domain)
    doublons_infos = []
    if not victim_domain:
        stdlog("Skipping doublon lookup : victim domain is empty or invalid.")
    else:
        for post in posts:
            post_domain = get_domain(post['website'])  # Extract domain from post['website']
            if post_domain and  victim_domain == post_domain and post['group_name'] != group_name:
                encoded_link = base64.b64encode(f"{post['post_title']}@{post['group_name']}".encode()).decode()
            
                infos = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "group": post['group_name'],
                    "link": f"https://www.ransomware.live/id/{encoded_link}",
                    "attackdate": post['published']
                }
            
                doublons_infos = [infos]
                published = post['published']
                stdlog(f"Duplicate found: {post['post_title']} in group {post['group_name']}")
                #break
    
    newpost = posttemplate(victim, group_name, now,description,clean_slug(website),published,post_url,country,activity,doublons_infos,extra_infos)
    posts.append(newpost)


    #extra = enrich_post(title, description)
    #print('Extra infos : ' + str(extra))


    with open(db_dir / 'victims.json', 'w', encoding='utf-8') as outfile:
        json.dump(posts, outfile, indent=4, ensure_ascii=False)

    victimtobluesky(victim,group_name,country)
    message = "<b>" + victim +  "</b> ("+ country + ") est victime du ransomware <b>" + group_name + "</b>"
    msgtoPushover(message)
    victimtonotify(victim,group_name,activity,country)

def get_domain(url):
    """Extracts domain name from a given URL, removing http(s):// and www."""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url  # Add default scheme to parse correctly
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # Extracts the domain
    return domain.replace('www.', '')  # Removes 'www.' if present

def country_code_to_flag(country_code):
    """
    Convert a 2-letter country code to its corresponding flag emoji.

    Args:
        country_code (str): A 2-letter ISO 3166-1 alpha-2 country code.

    Returns:
        str: The flag emoji for the country, or an error message if the code is invalid.
    """
    if not country_code.isalpha() or len(country_code) != 2:
        return ""

    # Convert the country code to uppercase for consistency
    country_code = country_code.upper()

    # Calculate the flag emoji using Unicode offset
    flag = "".join(chr(127397 + ord(char)) for char in country_code)
    flag = f" ({flag}) "
    return flag


def victimtobluesky(post_title,group,country=None):
    try:
        combined_string = f"{post_title}@{group}"
        uri = 'https://www.ransomware.live/id/'+base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')
        stdlog('Send Bluesky notification')
        url = os.environ.get('BLUESKY_URL')
        handle = os.environ.get('BLUESKY_HANDLE')
        password = os.environ.get('BLUESKY_APP_PASSWORD')
        resp = requests.post(url,
                    json={"identifier": handle, "password": password},
                )
        resp.raise_for_status()
        session = resp.json()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        text= "According to Ransomware.live, " + group + " ransomware group has added "
        startoffset = len(text)
        textend = post_title + country_code_to_flag(country) + " to its victims."
        endoffset = len(post_title) + startoffset
        text = text + textend
        post = {
                "$type": "app.bsky.feed.post",
                "text": text,
                "createdAt": now,
                "facets": [{
                    "index": {
                    "byteStart": startoffset,
                    "byteEnd": endoffset,
                    },
                "features": [{
                    "$type": "app.bsky.richtext.facet#link",
                    "uri": uri,
                    }],
                }],
            }
        resp = requests.post("https://bsky.social/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": "Bearer " + session["accessJwt"]},
                    json={
                        "repo": session["did"],
                        "collection": "app.bsky.feed.post",
                        "record": post,
                    },
            )
    except Exception as e:
        errlog(f'Error posting on bluesky : {e}')


def msgtoPushover(MESSAGE):
    try:
        stdlog('Send Pushover notification')
        USER_KEY=os.getenv('PUSH_USER')
        API_KEY= os.getenv('PUSH_API')
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
                "token": API_KEY,
                "user": USER_KEY,
                "message": MESSAGE,
                "html": 1
                }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
    except:
        errlog('Error sending Pushover notification')

def grouptobluesky(group):
    try:
        stdlog('Send Bluesky notification')
        url = os.environ.get('BLUESKY_URL')
        handle = os.environ.get('BLUESKY_HANDLE')
        password = os.environ.get('BLUESKY_APP_PASSWORD')
        resp = requests.post(url,
                    json={"identifier": handle, "password": password},
                )
        resp.raise_for_status()
        session = resp.json()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        text= "Ransomware.live is beginning to monitor a new ransomware group: " + group.capitalize() + "."
        startoffset = 64
        uri = "https://ransomware.live/group/" + group
        endoffset = len(text)-1 
            # Required fields that each post must include
        post = {
                "$type": "app.bsky.feed.post",
                "text": text,
                "createdAt": now,
                "facets": [{
                    "index": {
                    "byteStart": startoffset,
                    "byteEnd": endoffset,
                    },
                "features": [{
                    "$type": "app.bsky.richtext.facet#link",
                    "uri": uri,
                    }],
                }],
            }
        resp = requests.post("https://bsky.social/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": "Bearer " + session["accessJwt"]},
                    json={
                        "repo": session["did"],
                        "collection": "app.bsky.feed.post",
                        "record": post,
                    },
            )
    except Exception as e:
        errlog(f'Error posting on bluesky : {e}')



def iso2_to_country_name(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code.upper())
    return country.name if country else None


def victimtonotify(post_title, group, sector=None, country=None):
    try:
        # Build unique URI
        combined_string = f"{post_title}@{group}"
        uri = 'https://www.ransomware.live/id/' + base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')

        # Country handling
        countryname = None
        flag = ""
        country_code_clean = None
        if country:
            try:
                country_code_clean = country.upper()
                countryname = iso2_to_country_name(country_code_clean)
                flag = country_code_to_flag(country_code_clean)
            except Exception as e:
                errlog(f"[Country] Error converting {country} to name/flag: {e}")

        # Load env variables
        base_url = os.environ.get('NTFY_URL')
        token = os.environ.get('NTFY_TOKEN')
        if not base_url or not token:
            errlog("NTFY_URL or NTFY_TOKEN missing in environment")
            return
        base_url = base_url.rstrip('/')

        # Compose message and headers
        message = f"{post_title} {flag} has been claim by {group.capitalize()}"
        headers = {
            "X-Title": "New victim detected by Ransomware.live",
            "X-Tags": ",".join(filter(None, ["warning", sector, countryname])),
            "X-Click": uri,
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain",
            "User-Agent": "httpx"
        }
        #print('headers =', headers)
        stdlog(f"Sending notifications for {post_title} ({group})")

        with httpx.Client(http2=False, timeout=10.0) as client:
            # Send to /victims
            topic_victims = f"{base_url}/victims"
            response1 = client.post(topic_victims, content=message, headers=headers)
            if response1.status_code == 200:
                stdlog("✅ Notification sent to /victims")
            else:
                errlog(f"❌ Notification to /victims failed: {response1.status_code} - {response1.text}")

            # Send to /country_<code> if applicable
            
            if country_code_clean:
                topic_country = f"{base_url}/country_{country_code_clean.lower()}"
                response2 = client.post(topic_country, content=message, headers=headers)
                if response2.status_code == 200:
                    stdlog(f"✅ Notification sent to /country_{country_code_clean.lower()}")
                else:
                    errlog(f"❌ Notification to /country_{country_code_clean.lower()} failed: {response2.status_code} - {response2.text}")
            if sector:
                topic_country = f"{base_url}/sector_{sector.lower().replace(' / ','_').replace(' ','_')}"
                response2 = client.post(topic_country, content=message, headers=headers)
                if response2.status_code == 200:
                    stdlog(f"✅ Notification sent to /sector_{sector.lower().replace(' ','_')}")
                else:
                    errlog(f"❌ Notification to /sector_{sector.lower().replace(' ','_')} failed: {response2.status_code} - {response2.text}")
            topic_group = f"{base_url}/group_{group.lower()}"
            response3 = client.post(topic_group, content=message, headers=headers)
            if response3.status_code == 200:
                stdlog(f"✅ Notification sent to /group_{group.lower()}")
            else:
                errlog(f"❌ Notification to /group_{group.lower()} failed: {response3.status_code} - {response3.text}")
            
    except Exception as e:
        errlog(f"Unhandled exception in victimtonotify: {e}")
