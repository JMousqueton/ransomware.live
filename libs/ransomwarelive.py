import asyncio
import hashlib
import json
import os
import re
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import logging 
import lxml.html # Gettitle 
from PIL import Image, ImageDraw, ImageFilter
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
import http.client, urllib
# mail 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

# Appender 
import html
from gpt_query import GPTQuery
import notif 
import ia_detection 

## Hudsonrock 
import tldextract
import hudsonrock 

# Country 
import pycountry
import tldextract

# Import for update groups
import pandas as pd

## EXCEPTION 

CHROMIUM_PROXY_GROUPS = [
    "cactus",
    "hunters",
    "helldown",
    "trinity",
    "akira",
    "flocker",
    "metaencrytor",
    "blacksuit",
    "stormous",
    "BrainCipher",
    "incransom",
    "metaencrytor"
]

## TODO :
# STMPmail : make a variable for to:  

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

WATERMARK_IMAGE_PATH = os.getenv('WATERMARK_IMAGE_PATH')
POST_SCREENSHOT_DIR = os.getenv('POST_SCREENSHOT_DIR')
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR')
TOR_PROXY = {"server": os.getenv('TOR_PROXY_SERVER')}
#FF_PROXY_GROUPS = os.getenv('FF_PROXY_GROUPS').split(',')
DATA_DIR = os.getenv('DATA_DIR')
GROUPS_FILE = os.getenv('GROUPS_FILE')
VICTIMS_FILE = os.getenv('VICTIMS_FILE')

GPT = os.getenv('OPENAI_API_KEY')


PUSH_USER_KEY=os.getenv('PUSH_USER',None)
PUSH_API_KEY= os.getenv('PUSH_API',None)

GROUPS_FILE = DATA_DIR + GROUPS_FILE
VICTIMS_FILE = DATA_DIR + VICTIMS_FILE


############################
#
# Internal functions  
#
###########################

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
    )

def stdlog(msg):
    '''standard infologging'''
    logging.info(msg)

def dbglog(msg):
    '''standard debug logging'''
    logging.debug(msg)

def errlog(msg,pushover=False):
    logging.error(msg)
    load_dotenv()
    if PUSH_USER_KEY != None and PUSH_API_KEY!=None and pushover == True:
        stdlog('Send push notification')
        MESSAGE = "❌ " +  str(msg)
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
                "token": PUSH_API_KEY,
                "user": PUSH_USER_KEY,
                "message": MESSAGE,
                "html": 1
                }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()


def is_fqdn(string):
    # Regular expression pattern to validate FQDN
    fqdn_pattern = r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$"
    
    # Check if the string matches the FQDN pattern
    if re.match(fqdn_pattern, string):
        return True
    return False        

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
    if is_fqdn(victim):
        website = victim
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


def extract_fqdn(url):
    # Extract components using tldextract
    extract_result = tldextract.extract(url)
    
    # Exclude 'www' if it is the subdomain
    subdomain = '' if extract_result.subdomain == 'www' else extract_result.subdomain
    
    # Combine the extracted parts to form the FQDN
    fqdn = '.'.join(part for part in [subdomain, extract_result.domain, extract_result.suffix] if part)
    return fqdn


def openjson(file):
    '''
    opens a file and returns the json as a dict
    '''
    with open(file, encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    return data

def getsitetitle(html) -> str:
    '''
    tried to parse out the title of a site from the html
    '''
    stdlog('Getting site title')
    try:
        title = lxml.html.parse(html)
        titletext = title.find(".//title").text
        titletext = clean_string(titletext)
    except AssertionError:
        stdlog('Could not fetch site title from source - ' + str(html))
        return None
    except AttributeError:
        stdlog('Could not fetch site title from source - ' + str(html))
        return None
    # limit title text to 50 chars
    if titletext is not None:
        if len(titletext) > 50:
            titletext = titletext[:50]
        stdlog('Site title : ' + str(titletext))
        return titletext
    stdlog('Could not find site title from source - ' + str(html))
    return None

def md5_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def md5_file(file_path, chunk_size=8192):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def clean_string(s):
    s = clean_markdown(s)
    s = s.replace('[DISCLOSED]', '')  # Remove [DISCLOSED]
    s = s.replace('<Auction>','')
    s = s.replace('(SOLD)','')
    s = s.replace('<SOLD>','')
    s = s.replace('<Disclose>','')
    s = s.replace(', Updated data leak.','')
    s = s.replace('Updated','')
    s = s.replace('update','')
    s = s.replace('<disclose>','')
    if s.endswith(" PoC"):
        s = s[:-4]  # Remove the last 4 characters
    s = s.replace('<','')
    s = s.replace('>','')
    s = re.sub(' +', ' ', s)  # Replace multiple spaces with a single space
    s = s.replace('Data Leak', '')
    s = s.replace('pt.2', '')
    s = re.sub(' +', ' ', s)  # Replace multiple spaces with a single space
    s = s.strip() 
    return s

def clean_markdown(s):
    try:
        chars_to_remove='|\t\b\n\r'
        for char in chars_to_remove:
            s = s.replace(char, ' ')
        return s
    except:
        return s

def add_metadata(output):
    image = Image.open(output)
    metadata = PngInfo()
    metadata.add_text("Source", "Ransomware.live")
    metadata.add_text("Copyright", "Ransomware.live")
    metadata.add_text("Author", "Julien Mousqueton")
    current_date = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
    metadata.add_text("Creation Time", current_date)
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), current_date, fill=(0, 0, 0))
    stdlog(f'Add metadata to {output}')
    image.save(output, pnginfo=metadata)

def get_metadata(image_path):
    image = Image.open(image_path)
    if isinstance(image.info, dict):
        stdlog(f"Metadata for {image_path}:")
        for key, value in image.info.items():
            print(f"{key}: {value}")
    else:
        errlog(f"No metadata found for {image_path}")

def add_watermark(image_path, watermark_image_path=WATERMARK_IMAGE_PATH):
    """Adds a watermark image to the center of the input image."""
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

    stdlog(f'Add watermark to {image_path}')
    original.save(image_path, 'PNG')

def get_group_from_url(url):
    groups = openjson(GROUPS_FILE)
    for group in groups:
        for host in group['locations']:
            url = re.sub(r'^https?:\/\/', '', url)
            if url[:10] in host['fqdn']:
                return group['name']
    return None

def clean_slug(url):
    # Remove http://, https://, and trailing slashes
    cleaned_url = re.sub(r'^https?://|/$', '', url)
    return cleaned_url

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


def find_slug_by_md5(group_name, target_md5):
    # Load the JSON data from the file or source
    data = openjson(GROUPS_FILE)
    
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

def extract_md5_from_filename(file_name):
    parts = file_name.rsplit("-", 1)
    
    if len(parts) == 2:
        before_hyphen, after_hyphen = parts
        dot_position = after_hyphen.rfind(".")
        
        if dot_position != -1:
            extracted_text = after_hyphen[:dot_position]
            return extracted_text

def existingpost(post_title, group_name):
    '''
    check if a post already exists in victims.json
    '''
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        if post['post_title'].lower() == post_title.lower() and post['group_name'] == group_name:
            return True
    return False


def posttemplate(victim, group_name, timestamp,description,website,published,post_url,country,activity):
    schema = {
        'post_title': victim,
        'group_name': group_name,
        'discovered': timestamp,
        'description': description,
        'website': website,
        'published' : published,
        'post_url' : post_url,
        'country'   : country,
        'activity'  : activity
    }
    return schema

def isexception(victim, group):
    try:
        with open('exceptions.lst', 'r') as file:
            for line in file:
                # Split the line by comma and strip any surrounding whitespace
                line_victim, line_group = line.strip().split(';')
                if line_victim == victim and line_group == group:
                    return True
        return False
    except FileNotFoundError:
        errlog("The file 'exceptions.lst' was not found.")
        return False

def appender(post_title, group_name, description="", website="", published="", post_url="", country=""):
    '''
    append a new post to database
    '''
    if len(post_title) == 0:
        stdlog('post_title is empty')
        return
    if len(post_title) > 90:
        post_title = post_title[:90]
    post_title = html.unescape(post_title)
    post_title = clean_string(post_title)
    # Check exclusion 
    if isexception(post_title, group_name):
        stdlog('Exception found for ' + post_title)
        return
    if existingpost(post_title, group_name) is False:
        stdlog(f'adding new post - group: {group_name}  title: {post_title}   website: {website}')
        ## Post Infostealer information 
        if is_fqdn(post_title) and len(website) == 0:
            website = post_title
        if website:
            stdlog('Query Hudsonrock with ' + extract_fqdn(website))
            asyncio.run(hudsonrock.run_query(extract_fqdn(website)))
        posts = openjson(VICTIMS_FILE)
        if published:
            try:
                published_date = datetime.fromisoformat(published)
                if published_date > datetime.now():
                    published = str(datetime.now())
            except ValueError:
                stdlog('Invalid published date format')
                published = str(datetime.today())
        else:
            published = str(datetime.today())
        if GPT: 
            gpt_query = GPTQuery()
            prompt = f"Based on the International Standard Industrial Classification of All Economic Activities (ISIC) Revision 4, provide only the main activity sector of the company with the name or domain '{post_title}', without any additional text."
            activity = gpt_query.query(prompt)
        else:
            activity = '' 
        country = get_country(post_title,description,website)
        if GPT and len(country) < 2 :
            stdlog(f'Query GPT for "{post_title}" country')
            gpt_query = GPTQuery()
            prompt = f"I would like the 2 letters code of the country, and only the 2 letters not extra text, where the headquarter of this company is located {post_title}"
            country = gpt_query.query(prompt)
            if country:
                stdlog(f'Found : {country}')
        if GPT and description == '':
            stdlog(f'Query GPT for "{post_title}" description')
            gpt_query = GPTQuery()
            prompt = f'Can you provide a detailed description the company "{post_title}" in around 400 chars and without any links ?'
            description = gpt_query.query(prompt,topic='activity')
        if description == None:
            description = ''
        newpost = posttemplate(post_title, group_name, str(datetime.today()),description,clean_slug(website),published,post_url,country,activity)
        posts.append(newpost)
        with open(VICTIMS_FILE, 'w', encoding='utf-8') as outfile:
            json.dump(posts, outfile, indent=4, ensure_ascii=False)
        load_dotenv()
        if 'MS_TEAMS_WEBHOOK' in os.environ and os.environ['MS_TEAMS_WEBHOOK']:
            notif.toteams(newpost['post_title'], newpost['group_name'])
        if 'MASTODON_TOKEN' in os.environ and os.environ['MASTODON_TOKEN']:
            notif.toMastodon(post_title,group_name)
        if 'PUSH_API' in os.environ and os.environ['PUSH_API']:
            notif.toPushover(post_title, group_name)
        if 'BLUESKY_APP_PASSWORD' in os.environ and os.environ['BLUESKY_APP_PASSWORD']:
            notif.victimtobluesky(post_title, group_name)
        if 'MATTERMOST_WEBHOOK' in os.environ and os.environ['MATTERMOST_WEBHOOK']:
            notif.tomattermost(post_title, group_name)
        ### Post screenshot
        if post_url !="":
            stdlog('Call screenshotter for ' + post_url)
            hash_object = hashlib.md5(post_url.encode('utf-8'))
            hex_digest = hash_object.hexdigest()
            filename = os.path.join(POST_SCREENSHOT_DIR, f'{hex_digest}.png')
            asyncio.run(screenshot(post_url,filename))


def checkexisting(provider):
    '''
    check if group already exists within groups.json
    '''
    groups = openjson(GROUPS_FILE)
    for group in groups:
        if group['name'] == provider:
            return True
    return False

def creategroup(name, location):
    '''
    create a new group for a new provider - added to groups.json
    '''
    location = siteschema(location)
    insertdata = {
        'name': name,
        'captcha': bool(),
        'parser': bool(),
        'javascript_render': bool(),
        'meta': None,
        'description': None,
        'locations': [
            location
        ],
        'profile': list()
    }
    return insertdata

def siteschema(location):
    '''
    returns a dict with the site schema
    '''
    if not location.startswith('http'):
        dbglog('Ransomware.live: ' + 'assuming we have been given an fqdn and appending protocol')
        location = 'http://' + location
    schema = {
        'fqdn': getapex(location),
        'title': None,
        'version': 3,
        'slug': location,
        'available': False,
        'delay': None,
        'updated': None,
        'lastscrape': '2021-01-01 00:00:00.000000',
        'enabled': True
    }
    dbglog('Ransomware.live: ' + 'schema - ' + str(schema))
    return schema

def getapex(slug):
    '''
    returns the domain for a given webpage/url slug
    '''
    stripurl = tldextract.extract(slug)
    if stripurl.subdomain:
        return stripurl.subdomain + '.' + stripurl.domain + '.' + stripurl.suffix
    return stripurl.domain + '.' + stripurl.suffix


def get_ransomware_report(group, file_path):
    # Read the markdown file
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        errlog(f'File {file_path} not found')
        return None
    except Exception as e:
        errlog(f'An error occurred: {str(e)}')
        return None

    # Extract the lines that contain the table
    table_lines = [line.strip() for line in lines if '|' in line and '---' not in line]

    if not table_lines:
        errlog('No table found in the file.')
        return None

    # Parse the table data
    data = []
    for line in table_lines[1:]:  # Skip the header line
        columns = line.split('|')[1:-1]  # Split by '|' and ignore the first and last empty entries
        columns = [col.strip() for col in columns]
        if len(columns) == 3:  # Ensure that there are exactly three columns
            data.append(columns)

    if not data:
        errlog('No valid data found in the table.')
        return None

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Date Published", "Ransomware/Extortionist", "Report"])

    # Function to clean and extract all group names
    def extract_groups(text):
        text = text.lower()
        # Extract primary group and all aliases within parentheses
        if '(' in text and ')' in text:
            main_group, aliases = text.split('(', 1)
            aliases = aliases.rstrip(')').replace(' ', '').split(',')
            all_groups = [main_group.strip()] + aliases
        else:
            all_groups = [text.strip()]
        return all_groups

    # Apply the extraction function
    df['Group List'] = df['Ransomware/Extortionist'].apply(extract_groups)
    df['Group List'] = df['Group List'].astype(str).str.replace(" ", "").str.replace('international','')

    # Flatten the list of groups and match against the input
    cleaned_group = group.lower()


    df['Match'] = df['Group List'].apply(lambda groups: cleaned_group in groups)

    # Search for the group in the DataFrame
    result = df[df['Match']]

    # Return the report if found
    if not result.empty:
        return ' / '.join(f"{report}" for report in result['Report'].values)
        # return result['Report'].values[0]
    else:
        return None



def get_tools_by_group(ransomware_group, file_path):
    tools_by_group = {}
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except:
        return None
    # Parse the file to extract the tool and the associated threat groups
    for line in lines:
        if '|' in line and 'Tool Name' not in line:
            parts = [part.strip() for part in line.split('|') if part.strip()]
            if len(parts) == 2:
                tool_name = parts[0]
                threat_groups = [group.strip().lower().replace(' ','') for group in parts[1].split(',')]
                tools_by_group[tool_name] = threat_groups

    # Filter tools by the specified ransomware group
    tools_used = [tool for tool, groups in tools_by_group.items() if ransomware_group in groups]

    return tools_used

import json

def update_groups_intel():
    # Load the JSON data from the file
    with open('./data/groups.json', 'r') as json_file:
        groups_data = json.load(json_file)

    # Mapping for group name corrections
    group_name_mapping = {
        'lockbit': 'lockbit_old',
        'lockbit3': 'lockbit',
        'vicesociety': 'vice'
    }

    # File paths for reports
    report_files = [
        './import/Ransomware-Tool-Matrix/ThreatIntel/CISAThreatGroups.md',
        './import/Ransomware-Tool-Matrix/ThreatIntel/TrendMicroThreatGroups.md',
        './import/Ransomware-Tool-Matrix/ThreatIntel/TheDFIRReportGroups.md',
        './import/Ransomware-Tool-Matrix/ThreatIntel/ExtraThreatIntel.md'
    ]

    # Check each group for a StopRansomware report and replace the profile if found
    for group in groups_data:
        group_name = group['name'].lower()
        group_name = group_name_mapping.get(group_name, group_name)  # Apply name correction if needed

        group['profile'] = []

        for report_file in report_files:
            report = get_ransomware_report(group_name, report_file)
            if report:
                report_entries = report.split(' / ')
                group['profile'].extend(report_entries)

    # Save the updated JSON back to a file
    with open('./data/groups.json', 'w') as json_file:
        json.dump(groups_data, json_file, indent=4)

    stdlog("Groups updated successfully.")



############################
#
# Tools functions 
#
###########################

def remove_duplicate_files(directory):
    files_hash = {}
    duplicates = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_hash = md5_file    (file_path)
            
            if file_hash in files_hash:
                duplicates.append(file_path)
            else:
                files_hash[file_hash] = file_path

    for duplicate in duplicates:
        os.remove(duplicate)
        stdlog("Removed duplicate file: " + duplicate.replace(directory,''))

def order_group():
    try:
        # Load the JSON file
        with open(GROUPS_FILE, 'r') as f:
            data = json.load(f)
        # Sort the data by name, ignoring case
        sorted_data = sorted(data, key=lambda x: x['name'].lower())
        # Save the sorted data back to the same JSON file
        with open(GROUPS_FILE, 'w') as f:
            json.dump(sorted_data, f, indent=4)
        stdlog(f"Groups Database has been sorted")
    except Exception as e:
        errlog(f"An error occurred: {e}")


def blur_image(input_path, output_path, blur_radius=5):
    try:
        # Open the input image
        img = Image.open(input_path)
        
        # Apply Gaussian blur with the specified radius
        blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Get the directory and filename from the input path
        directory, filename = os.path.split(output_path)
        
        # Generate the new path for the blurred image
        output_path = os.path.join(directory,filename)
        
        # Save the blurred image to the output path
        blurred_img.save(output_path)
        
        stdlog(f"Image blurred successfully")
    except Exception as e:
        errlog(f"An error occurred: {e}")

def rename_original_image(input_path):
    try:
        # Get the directory and filename from the input path
        directory, filename = os.path.split(input_path)
        
        # Generate the new name for the original image
        new_name = os.path.splitext(filename)[0] + "-ORIG.png"
        
        # Create the new path for the renamed original image
        new_path = os.path.join(directory, new_name)
        
        # Rename the original image
        os.rename(input_path, new_path)
        
        dbglog(f"Original image renamed to {new_name}")
        return new_path
    except Exception as e:
        errlog(f"An error occurred while renaming the original image: {e}")
        return None

############################
#
# Main functions 
#
###########################
 

async def scrape(force=False):
    groups = openjson(GROUPS_FILE)
    slug_count = sum(len(group["locations"]) for group in groups)
    counter = 0 
    for group in groups:
        stdlog(f'Scraper is working on {group["name"]}')
        for host in group['locations']:
            counter += 1
            stdlog(f'[{counter}/{slug_count}]Scraping {host["slug"]}')
            if not host['enabled'] and force == False:
                stdlog('Skipping disabled host')
                continue
            filename = f"source/{group['name']}-{md5_hash(host['slug'])}.html"
            async with async_playwright() as p:
                try: 
                    if group['name'] in CHROMIUM_PROXY_GROUPS:
                        stdlog(f"Using Chromium with TOR proxy for {group['name']}")
                        browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
                    elif ".onion" in host["slug"]:
                        stdlog(f"Using Firefox with TOR proxy for {group['name']}")
                        browser = await p.firefox.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
                    else:
                        stdlog(f"Clearweb connexion for {group['name']}")
                        browser = await p.firefox.launch(args=['--ignore-certificate-errors'])
                    context = await browser.new_context(ignore_https_errors=True)
                    page = await context.new_page()
                    await page.goto(host["slug"],timeout=60000)
                    await page.wait_for_timeout(10000)  # Wait for the page to fully load and execute JavaScript
                    html = await page.content()
                    with open(filename, 'w', encoding='utf-8') as file:
                        file.write(html)
                    host.update({
                            'available': True,
                            'title': getsitetitle(filename),
                            'lastscrape': str(datetime.today()),
                            'updated': str(datetime.today())
                        })
                    updated = True
                    await browser.close()
                except Exception as e:
                    host.update({
                            'available': False,
                            'updated': str(datetime.today())
                        })
                    updated = True
                    errlog(f'Scrapping failled for {host["slug"]} with error : {e}')
            if updated:
                with open(GROUPS_FILE, 'w', encoding='utf-8') as groupsfile:
                    json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
                stdlog(f'Group {group["name"]} metadata updated')


async def scrapegang(groupname,force=False):
    groups = openjson(GROUPS_FILE)
    for group in groups:
        if group['name'] == groupname:
            stdlog(f'Scraper is working on {group["name"]}')
            for host in group['locations']:
                stdlog(f'Scraping {host["slug"]}')
                if not host['enabled'] and force == False:
                    stdlog('Skipping disabled host')
                    continue
                filename = f"source/{group['name']}-{md5_hash(host['slug'])}.html"
                async with async_playwright() as p:
                    try: 
                        if group['name'] in CHROMIUM_PROXY_GROUPS:
                            stdlog(f"Using Chromium with TOR proxy for {group['name']}")
                            browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
                        elif ".onion" in host["slug"]:
                            stdlog(f"Using Firefox with TOR proxy for {group['name']}")
                            browser = await p.firefox.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
                        else:
                            stdlog(f"Clearweb connexion for {group['name']}")
                            browser = await p.firefox.launch(args=['--ignore-certificate-errors'])
                        context = await browser.new_context()
                        page = await context.new_page()
                        await page.goto(host["slug"])
                        await page.wait_for_timeout(10000)  # Wait for the page to fully load and execute JavaScript
                        html = await page.content()
                        with open(filename, 'w', encoding='utf-8') as file:
                            file.write(html)
                        host.update({
                            'available': True,
                            'title': getsitetitle(filename),
                            'lastscrape': str(datetime.today()),
                            'updated': str(datetime.today())
                        })
                        updated = True
                        await browser.close()
                    except Exception as e:
                        host.update({
                            'available': False,
                            'updated': str(datetime.today())
                        })
                        updated = True
                        errlog(f'Scrapping failled for {host["slug"]} with error : {e}')
                    if updated:
                        with open(GROUPS_FILE, 'w', encoding='utf-8') as groupsfile:
                            json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
                        stdlog(f'Group {group["name"]} metadata updated')
                    

async def screenshot(url,filename):
    async with async_playwright() as p:
        try:
            fqdn = extract_fqdn(url)
            group = get_group_from_url(fqdn)
            if group == None:
                group = url 
            if group in CHROMIUM_PROXY_GROUPS:
                stdlog(f"Using Chromium with TOR proxy for {group}")
                browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
            elif ".onion" in url:
                stdlog(f"Using Firefox with TOR proxy for {group}")
                browser = await p.firefox.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
            else:
                stdlog(f"Clearweb connexion for {group}")
                browser = await p.firefox.launch(args=['--ignore-certificate-errors'])
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url,timeout=60000)
            await page.mouse.move(x=500, y=400)
            await page.mouse.wheel(delta_y=2000, delta_x=0)
            await page.wait_for_timeout(50000)  # Wait for the page to fully load and execute JavaScript
        
            await page.screenshot(path=filename,full_page=True)
            """
            if group == "bianlian":
                stdlog('Exception for bianlian')
                await page.screenshot(path=filename,full_page=True)
            else:

                # Get the total height of the page
                total_height = await page.evaluate('''() => {
                    return document.body.scrollHeight;
                }''')
                viewport_height = await page.evaluate('''() => {
                    return window.innerHeight;
                }''')
                
                # Take screenshots in segments
                segment_filenames = []
                offset = 0
                while offset < total_height:
                    await page.evaluate(f'''window.scrollTo(0, {offset});''')
                    await page.wait_for_timeout(1000)  # Wait for scrolling to finish
                    segment_filename = f"{filename}_segment_{offset}.png"
                    await page.screenshot(path=segment_filename, clip={'x': 0, 'y': 0, 'width': 1280, 'height': viewport_height})
                    segment_filenames.append(segment_filename)
                    offset += viewport_height
                
                await browser.close()
                
                # Stitch the images together
                images = [Image.open(seg) for seg in segment_filenames]
                total_width = images[0].width
                total_height = sum(img.height for img in images)
                
                stitched_image = Image.new('RGB', (total_width, total_height))
                y_offset = 0
                for img in images:
                    stitched_image.paste(img, (0, y_offset))
                    y_offset += img.height
                
                stitched_image.save(filename)
                
                # Cleanup segment files
                for seg in segment_filenames:
                    os.remove(seg)
            """
            
            stdlog(f"Screenshot of {url} has been saved to {filename}")
            await browser.close()
            facedetectionexception = [
                'incransom',
                'ransomhouse'
            ]
            if ia_detection.check_image_for_face(filename) and group not in facedetectionexception:
                        body="A new screenshot must be analysed : \n\n https://www.ransomware.live/screenshots/posts/"+os.path.basename(filename)
                        send_email("[Action Required] Check this screenshot for any ID",body, "support@ransomwarelive.freshdesk.com",filename)
            add_metadata(filename)
            add_watermark(filename)
        except Exception as e:
            errlog(f"Screenshot of {url} has failled with error: {e}")


async def screenshotgangs():
    groups = openjson(GROUPS_FILE)
    for group in groups:
        stdlog(f'Screenshotter is working on {group["name"]}')
        for host in group['locations']:
            stdlog(f'Screenshot {host["slug"]}')
            if not host['enabled']:
                stdlog('Skipping disabled host')
                continue
            filename = clean_slug(host["fqdn"]).replace(".", "-")
            filename = f'{SCREENSHOT_DIR}/{filename}.png'
            async with async_playwright() as p:
                try:
                    #browser = await p.firefox.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"})
                    if group['name'] in CHROMIUM_PROXY_GROUPS:
                        stdlog(f"Using Chromium with TOR proxy for {group['name']}")
                        browser = await p.chromium.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
                    elif ".onion" in host["slug"]:
                        stdlog(f"Using Firefox with TOR proxy for {group['name']}")
                        browser = await p.firefox.launch(headless=True, proxy={"server": "socks5://127.0.0.1:9050"}, args=['--ignore-certificate-errors'])
                    else:
                        stdlog(f"Clearweb connexion for {group['name']}")
                        browser = await p.firefox.launch(args=['--ignore-certificate-errors'])
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto(host["slug"],timeout=60000)
                    await page.mouse.move(x=500, y=400)
                    await page.mouse.wheel(delta_y=2000, delta_x=0)
                    await page.wait_for_timeout(50000)  # Wait for the page to fully load and execute JavaScript
                    await page.screenshot(path=filename,full_page=True)
                    stdlog(f'Screenshot of {host["slug"]} has been saved to {filename}')
                    await browser.close()
                    add_metadata(filename)
                    add_watermark(filename)
                except Exception as e:
                    errlog(f'Screenshot of {host["slug"]} has failled with error {e}')
                stdlog(f'Finished screenshot{host["slug"]} for {group["name"]}')

def searchvictim(name):
    with open(VICTIMS_FILE, 'r') as file:
        data = json.load(file)
        
        # Ensure data is a list
        if not isinstance(data, list):
            data = [data]
        
        # Search logic

        matching_posts = [
            post for post in data if (
                name.lower() in post.get('website', '').lower() or 
                name.lower() in post.get('post_title', '').lower()
            )
        ]
        
        total_matches = len(matching_posts)
        
        # Print matching posts with counter
        for idx, post in enumerate(matching_posts, start=1):
            if post.get('post_url',None) is not None:

                hash_object = hashlib.md5()
                # Update the hash object with the string
                hash_object.update(post['post_url'].encode('utf-8'))
                # Get the hexadecimal representation of the hash
                hex_digest = hash_object.hexdigest()
                if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                    screenshot = "\033[1m Screenshot:\033[0m https://images.ransomware.live/screenshots/posts/" + hex_digest+'.png\n'
                else:
                    screenshot = ''
            print(f"[{idx}/{total_matches}]")
            print("\033[1m Post Title:\033[0m ", post.get('post_title', '\033[3mN/A\033[0m'))
            print("\033[1m Group Name:\033[0m ", post.get('group_name', '\033[3mN/A\033[0m'))
            print("\033[1m Discovered:\033[0m ", post.get('discovered', '\033[3mN/A\033[0m'))
            print("\033[1m Description:\033[0m ", post.get('description', '\033[3mN/A\033[0m'))
            if is_fqdn(post.get('post_title')):
                print("\033[1m Domain:\033[0m ", post.get('post_title', '\033[3mN/A\033[0m'))
                website = post.get('post_title')
            elif post.get('website') and is_fqdn(post.get('website')):
                print("\033[1m Domain:\033[0m ", post.get('website', '\033[3mN/A\033[0m'))
                website = post.get('website')
            else:
                website = post.get('website')
                print("\033[1m Website:\033[0m ", post.get('website', '\033[3mN/A\033[0m'))
            print("\033[1m Published:\033[0m ", post.get('published', '\033[3mN/A\033[0m'))
            print("\033[1m Post URL:\033[0m ", post.get('post_url', '\033[3mN/A\033[0m'))
            print(screenshot,end=" ")
            print("\033[1mCountry:\033[0m " +  post.get('country', '\033[3mN/A\033[0m'))
            print("\033[1m Activity:\033[0m ", post.get('activity', '\033[3mN/A\033[0m'))
            print("\033[1m Infostealer:\033[0m ", search_domain_for_infostealer(website))
            print( "-"*50)


def siteadder(name, location):
    '''
    handles the addition of new providers to groups.json
    '''
    if checkexisting(name):
        stdlog('Ransomware.live: ' + 'records for ' + name + ' already exist, appending to avoid duplication')
        siteappender(args.name, args.location)
    else:
        groups = openjson(GROUPS_FILE)
        newrec = creategroup(name, location)
        groups.append(dict(newrec))
        with open(GROUPS_FILE, 'w', encoding='utf-8') as groupsfile:
            json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
        notif.grouptobluesky(name)
        stdlog('Ransomware.live : ' + 'record for ' + name + ' added to Group Database')


def siteappender(name, location):
    '''
    handles the addition of new mirrors and relays for the same site
    to an existing group within groups.json
    '''
    groups = openjson(GROUPS_FILE)
    success = bool()
    for group in groups:
        if group['name'] == name:
            group['locations'].append(siteschema(location))
            success = True
    if success:
        with open(GROUPS_FILE, 'w', encoding='utf-8') as groupsfile:
            json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
    else:
        errlog('Ransomware.live : Cannot append to non-existing provider')


def search_domain_for_infostealer(domain):
    if domain:
        hr_file = DATA_DIR + 'hudsonrock.json'
        try:
            extracted = tldextract.extract(domain)
            fqdn = f"{extracted.domain}.{extracted.suffix}"
            data = openjson(hr_file)
            if fqdn in data:
                result = fqdn + ' ' + str(data[fqdn])
                return result
        except:
            return " Not information found in the database."


def ttps2json(input_directory, output_file):
    """
    Converts all .md files in the input_directory into a JSON file.
    Each file's data is stored in a list named after the filename (without .md).
    The file "MostUsedTools.md" is excluded from processing.
    Group names are transformed to lowercase, spaces are removed, 
    and "lockbit" is renamed to "lockbit3".
    
    Parameters:
    - input_directory: Directory containing the .md files.
    - output_file: The path where the resulting JSON file will be saved.
    """
    # Initialize a dictionary to store the data
    data = {}

    # Function to process each file and append data to the dictionary
    def process_file(file_path, list_name):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Find the start of the table and skip the title and separation lines
        table_started = False
        for line in lines:
            if '|' in line:
                if not table_started:
                    table_started = True
                    continue  # Skip the title line
                if line.strip().startswith('|---'):
                    continue  # Skip the separation line
                columns = line.strip().split('|')
                if len(columns) > 2:
                    tool = columns[1].strip()
                    groups = columns[2].strip()
                    groups = [transform_group_name(group.strip().replace('*', '')) for group in groups.split(',')]

                    for group in groups:
                        if group not in data:
                            # Initialize the group with empty lists for each potential category
                            data[group] = {name.replace('.md', ''): [] for name in os.listdir(input_directory) if name.endswith('.md') and name != "MostUsedTools.md"}
                        if tool not in data[group][list_name]:
                            data[group][list_name].append(tool)

    # Function to transform the group name
    def transform_group_name(group_name):
        # Convert to lowercase
        group_name = group_name.lower()
        # Remove spaces
        group_name = group_name.replace(' ', '')
        # Rename "lockbit" to "lockbit3"
        if group_name == "lockbit":
            group_name = "lockbit3"
        return group_name

    # Process each .md file in the directory, excluding "MostUsedTools.md"
    for filename in os.listdir(input_directory):
        if filename.endswith('.md') and filename != "MostUsedTools.md":
            filepath = os.path.join(input_directory, filename)
            list_name = filename.replace('.md', '')
            process_file(filepath, list_name)

    # Convert the dictionary into the desired list of dictionaries
    json_data = [{"group_name": group, **details} for group, details in data.items()]

    # Write the JSON data to the output file
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    stdlog(f'JSON data has been written to {output_file}')

