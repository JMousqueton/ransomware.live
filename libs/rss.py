import json
from datetime import datetime
import hashlib, os
from xml.etree.ElementTree import Element, SubElement, tostring
import html
import xml.sax.saxutils as saxutils
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

DATA_DIR = os.getenv('DATA_DIR')
VICTIMS_FILE = os.getenv('VICTIMS_FILE')

###
VICTIMS_FILE = DATA_DIR + VICTIMS_FILE

def md5GUID(input_string):
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()

def generate_rss_feed():
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
    image_url.text = 'https://www.ransomware.live/ransomwarelive.png'
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
        item_link.text = 'https://www.ransomware.live/#/group/{}'.format(item['group_name'])
        
        item_description = SubElement(rss_item, 'description')
        description_text = html.escape(item['description'])

        item_description.text = description_text
        if item.get('post_url'):
            md5_hash = hashlib.md5(item['post_url'].encode()).hexdigest()
            image_url = f"https://images.ransomware.live/screenshots/posts/{md5_hash}.png"
            image_path = f"./docs/screenshots/posts/{md5_hash}.png"
            if os.path.exists(image_path):
                image_size = os.path.getsize(image_path)
                enclosure = SubElement(rss_item, 'enclosure')
                enclosure.set('url', image_url)
                enclosure.set('type', 'image/png')
                enclosure.set('length', str(image_size))
            else:
                image_url = f"https://www.ransomware.live/ransomwarelive.png"
                image_path = f"./docs/ransomwarelive.png"
                image_size = os.path.getsize(image_path)
                enclosure = SubElement(rss_item, 'enclosure')
                enclosure.set('url', image_url)
                enclosure.set('type', 'image/png')
                enclosure.set('length', str(image_size))
        else:
            image_url = f"https://www.ransomware.live/ransomwarelive.png"
            image_path = f"./docs/ransomwarelive.png"
            image_size = os.path.getsize(image_path)
            enclosure = SubElement(rss_item, 'enclosure')
            enclosure.set('url', image_url)
            enclosure.set('type', 'image/png')
            enclosure.set('length', str(image_size))
        
        item_guid = SubElement(rss_item, 'guid')
        item_guid.text = 'https://www.ransomware.live/#/group/' + str(item['group_name']) + '?' + md5GUID(item_title.text)
        
        country = item.get('country', 'N/A')
        category_element = SubElement(rss_item, 'category')
        category_element.text = country if country else 'N/A'
        
        date_iso = item['discovered']
        date_rfc822 = datetime.strptime(date_iso, '%Y-%m-%d %H:%M:%S.%f').strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        item_pubdate = SubElement(rss_item, 'pubDate')
        item_pubdate.text = date_rfc822

    # Convert RSS object to string and save to file
    rss_str = tostring(rss, encoding='unicode')
    with open('./docs/rss.xml', 'w') as f:
        f.write(rss_str)
