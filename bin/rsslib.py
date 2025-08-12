import json
from datetime import datetime
import hashlib, os
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
# import xml.etree.ElementTree as ET
import html
import xml.sax.saxutils as saxutils
from dotenv import load_dotenv
import requests
import pytz
from shared_utils import  stdlog, errlog 
from pathlib import Path
import base64

# Load environment variables from ../.env
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
# Paths from environment variables
home = os.getenv("RANSOMWARELIVE_HOME")
db_dir = Path(home + os.getenv("DB_DIR"))
data_dir = Path(home + os.getenv("DATA_DIR"))
###
VICTIMS_FILE = db_dir / 'victims.json'

def md5GUID(input_string):
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()

def generate_victims_feed():
    # Load data from JSON file
    with open(VICTIMS_FILE) as f:
        data = json.load(f)

    data.sort(key=lambda item: datetime.strptime(item['discovered'], '%Y-%m-%d %H:%M:%S.%f'))

    # Create RSS element
    rss = Element('rss', {'version': '2.0', 'xmlns:atom': 'http://www.w3.org/2005/Atom'})

    # Create channel element
    channel = SubElement(rss, 'channel')
    title = SubElement(channel, 'title')
    title.text = 'Ransomware.live RSS Feed'
    link = SubElement(channel, 'link')
    link.text = 'https://www.ransomware.live/rss.xml'
    description = SubElement(channel, 'description')
    description.text = 'Last 100 entries monitoring by Ransomware.live'

    image = SubElement(channel, 'image')
    image_url = SubElement(image, 'url')
    image_url.text = 'https://images.ransomware.live/ransomwarelive.png'
    image_title = SubElement(image, 'title')
    image_title.text = 'Ransomware.live RSS Feed'
    image_link = SubElement(image, 'link')
    image_link.text = 'https://www.ransomware.live/rss.xml'

    # Add atom:link element
    atom_link = SubElement(channel, 'atom:link', href='https://www.ransomware.live/rss.xml', rel='self', type='application/rss+xml')

    # Iterate over data and create RSS items
    for i in reversed(range(len(data)-200, len(data))):
        item = data[i]
        rss_item = SubElement(channel, 'item')
        item_title = SubElement(rss_item, 'title')

        item_title.text = "🏴‍☠️ " + str(item['group_name']).capitalize() + " has just published a new victim : " + str(item['post_title']).replace('&amp;', '&')
        item_link = SubElement(rss_item, 'link')
        combined_string = f"{item['post_title']}@{item['group_name']}"
        item_link.text  = 'https://www.ransomware.live/id/' + base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')
        
        item_description = SubElement(rss_item, 'description')
        try:
            description_text = html.escape(item['description'])
        except:
            description_text = item['description']

        item_description.text = description_text
        if item.get('post_url'):
            md5_hash = hashlib.md5(item['post_url'].encode()).hexdigest()
            image_url = f"https://images.ransomware.live/victims/{md5_hash}.png"
            image_path = f"../images/victims/{md5_hash}.png"
            if os.path.exists(image_path):
                image_size = os.path.getsize(image_path)
                enclosure = SubElement(rss_item, 'enclosure')
                enclosure.set('url', image_url)
                enclosure.set('type', 'image/png')
                enclosure.set('length', str(image_size))
            else:
                image_url = f"https://images.ransomware.live/ransomwarelive.png"
                image_path = f"../images/ransomwarelive.png"
                image_size = os.path.getsize(image_path)
                enclosure = SubElement(rss_item, 'enclosure')
                enclosure.set('url', image_url)
                enclosure.set('type', 'image/png')
                enclosure.set('length', str(image_size))
        else:
            image_url = f"https://images.ransomware.live/ransomwarelive.png"
            image_path = f"../images/ransomwarelive.png"
            image_size = os.path.getsize(image_path)
            enclosure = SubElement(rss_item, 'enclosure')
            enclosure.set('url', image_url)
            enclosure.set('type', 'image/png')
            enclosure.set('length', str(image_size))
        
        item_guid = SubElement(rss_item, 'guid')
        item_guid.text = 'https://www.ransomware.live/group/' + str(item['group_name']) + '?' + md5GUID(item_title.text)
        
        country = item.get('country', 'N/A')
        category_element = SubElement(rss_item, 'category')
        category_element.text = country if country else 'N/A'
        
        date_iso = item['discovered']
        date_rfc822 = datetime.strptime(date_iso, '%Y-%m-%d %H:%M:%S.%f').strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        item_pubdate = SubElement(rss_item, 'pubDate')
        item_pubdate.text = date_rfc822

    # Convert RSS object to string and save to file
    rss_str = tostring(rss, encoding='unicode')
    with open(f'{data_dir}/rss.xml', 'w') as f:
        f.write(rss_str)
    stdlog('Victims Feed : ' + 'generated')


def generate_cyberattacks_feed():
    # URL containing the JSON data
    url = 'https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json'
    image_directory = '../images/news/'

    # Fetch data from the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Load JSON data
        json_data = json.loads(response.text)

        # Sort items by date
        sorted_data = sorted(json_data, key=lambda x: x['date'], reverse=True)[:100]

        # Create the XML structure
        rss = Element('rss', {'version': '2.0', 'xmlns:atom': 'http://www.w3.org/2005/Atom'})
        channel = SubElement(rss, 'channel')

        # Add Channel title
        title = SubElement(channel, 'title')
        title.text = "Ransomware.live: Last Cyber attacks Feed"

        # Add Channel link
        link = SubElement(channel, 'link')
        link.text = "https://www.ransomware.live/recentcyberattacks"

        # Add Channel description
        description = SubElement(channel, 'description')
        description.text = "Last 100 cyber attacks monitoring by Ransomware.live"
    
        # Add Channel image
        image = SubElement(channel, 'image')
        image_url = "https://www.ransomware.live/ransomwarelive.png"
        SubElement(image, 'url').text = image_url
        SubElement(image, 'title').text = "Ransomware.live: Last Cyber attacks Feed"
        SubElement(image, 'link').text = "https://www.ransomware.live/recentcyberattacks"

        # Add atom:link element
        atom_link = SubElement(channel, 'atom:link', href='https://www.ransomware.live/cyberattacks.xml', rel='self', type='application/rss+xml')

        # Add RSS elements for each sorted item
        for item in sorted_data:
            try:
                rss_item = SubElement(channel, 'item')
                SubElement(rss_item, 'title').text = item['title'] + ' ('+ item['country'] + ')'
                SubElement(rss_item, 'description').text = '(' + item['domain'] + ') ' + item['summary']
                combined_string = f"{item['domain'] }@{item['date'] }"
                link = base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')
                SubElement(rss_item, 'link').text = 'https://www.ransomware.live/press#' + link

                # Convert date to RFC-822 format with GMT timezone
                date_str = item['date']
                datetime_obj = datetime.strptime(date_str, '%Y-%m-%d')
                datetime_obj = pytz.utc.localize(datetime_obj)  # Set the timezone to GMT
                rfc_822_date = datetime_obj.strftime('%a, %d %b %Y %H:%M:%S %z')
                SubElement(rss_item, 'pubDate').text = rfc_822_date

                #item_image_url = f"https://logo.clearbit.com/{item['domain']}"
                #SubElement(rss_item, 'enclosure', attrib={
                #                'url': item_image_url, 'type': 'image/png'})

                item_guid = SubElement(rss_item, 'guid')
                item_guid.text = 'https://www.ransomware.live/?=' +md5GUID(item['title'])
            except:
                print('error')
        # Create an ElementTree object and write to the file in ./docs directory
        file_path = f'{data_dir}/cyberattacks.xml'
        tree = ElementTree(rss)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        stdlog('Cyber attacks Feed : ' + 'generated')
    else:
        stdlog("Failed to fetch data:", response.status_code)


