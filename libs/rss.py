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
from ransomwarelive import  stdlog, errlog 

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

DATA_DIR = os.getenv('DATA_DIR')
VICTIMS_FILE = os.getenv('VICTIMS_FILE')

###
VICTIMS_FILE = DATA_DIR + VICTIMS_FILE

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
    stdlog('Victims Feed : ' + 'generated')


def generate_cyberattacks_feed():
    # URL containing the JSON data
    url = 'https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json'
    image_directory = './docs/screenshots/news/'

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
        link.text = "https://www.ransomware.live/#/recentcyberattacks"

        # Add Channel description
        description = SubElement(channel, 'description')
        description.text = "Last 100 cyber attacks monitoring by Ransomware.live"
    
        # Add Channel image
        image = SubElement(channel, 'image')
        image_url = "https://www.ransomware.live/ransomwarelive.png"
        SubElement(image, 'url').text = image_url
        SubElement(image, 'title').text = "Ransomware.live: Last Cyber attacks Feed"
        SubElement(image, 'link').text = "https://www.ransomware.live/#/recentcyberattacks"

        # Add atom:link element
        atom_link = SubElement(channel, 'atom:link', href='https://www.ransomware.live/cyberattacks.xml', rel='self', type='application/rss+xml')

        # Add RSS elements for each sorted item
        for item in sorted_data:
            rss_item = SubElement(channel, 'item')
            SubElement(rss_item, 'title').text = item['title'] + ' ('+ item['country'] + ')'
            SubElement(rss_item, 'description').text = '(' + item['domain'] + ') ' + item['summary']
            SubElement(rss_item, 'link').text = 'https://www.ransomware.live/redirect.html?url=' + item['url']

            # Convert date to RFC-822 format with GMT timezone
            date_str = item['date']
            datetime_obj = datetime.strptime(date_str, '%Y-%m-%d')
            datetime_obj = pytz.utc.localize(datetime_obj)  # Set the timezone to GMT
            rfc_822_date = datetime_obj.strftime('%a, %d %b %Y %H:%M:%S %z')
            SubElement(rss_item, 'pubDate').text = rfc_822_date

            # Calculate MD5 hash of the link
            link_md5 = hashlib.md5(item['url'].encode()).hexdigest()
            image_path = os.path.join(image_directory, f"{link_md5}.png")

            # Check if the image exists for the item
            if os.path.exists(image_path):
                item_image_url = f"https://www.ransomware.live/screenshots/news/{link_md5}.png"
                image_size = os.path.getsize(image_path)
                SubElement(rss_item, 'enclosure', attrib={
                            'url': item_image_url, 'type': 'image/png', 'length': str(image_size)})

            item_guid = SubElement(rss_item, 'guid')
            item_guid.text = 'https://www.ransomware.live/?=' +md5GUID(item['title'])

        # Create an ElementTree object and write to the file in ./docs directory
        file_path = './docs/cyberattacks.xml'
        tree = ElementTree(rss)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        stdlog('Cyber attacks Feed : ' + 'generated')
    else:
        stdlog("Failed to fetch data:", response.status_code)

def generare_nego_feed():
    #Chargez les données du fichier JSON
    directory_path = '/var/www/ransomware-ng/import/'

    # Créez l'élément rss et ajoutez-y les attributs nécessaires
    rss = Element('rss', {'version': '2.0', 'xmlns:atom': 'http://www.w3.org/2005/Atom'})

    # Créez l'élément channel et ajoutez-y les éléments enfants nécessaires
    channel = SubElement(rss, 'channel')
    title = SubElement(channel, 'title')
    title.text = 'Ransomware.live Negotiations Feed'
    link = SubElement(channel, 'link')
    link.text = 'https://www.ransomware.live/negotiations.xml'
    description = SubElement(channel, 'description')
    description.text = 'Negotiations feed from Ransomware.live'

    image = SubElement(channel, 'image')
    image_url = SubElement(image, 'url')
    image_url.text = 'https://www.ransomware.live/ransomwarelive.png'
    image_title = SubElement(image, 'title')
    image_title.text = 'Ransomware.live Negotiations Feed'
    image_link = SubElement(image, 'link')
    image_link.text = 'https://www.ransomware.live/negotiations.xml'

    # Add atom:link element
    atom_link = SubElement(channel, 'atom:link', href='https://www.ransomware.live/negotiations.xml', rel='self', type='application/rss+xml')

    # Parcourez les données du fichier JSON et ajoutez un élément item pour chaque enregistrement
    for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".json"):
                    json_file = os.path.join(root, file)

                    # Extract file information
                    file_name = os.path.basename(json_file)
                    negotiation_name = file_name.replace('.json','')
                    file_path = os.path.abspath(json_file)
                    group = os.path.basename(os.path.dirname(file_path)).lower()
                    file_modified_time = os.path.getmtime(json_file)
                    meta_file = file_path.replace('.json','.meta')
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r') as file:
                            content = file.read()
                            meta_info = content.split(';')[0]
                            meta_info = "Initial ransom was " + meta_info
                    else:
                        meta_info = "No information available"


                    # Read the file modification date
                    modified_date = datetime.fromtimestamp(file_modified_time).isoformat()
                    rss_item = SubElement(channel, 'item')
                    item_title = SubElement(rss_item, 'title')
                    item_title.text = "A new negotiation chat from " + str(group) + " called " + str(negotiation_name).replace('_','.') + " has been added to Ransomare.live"
                    item_link = SubElement(rss_item, 'link')
                    item_link.text = 'https://www.ransomware.live/#/negotiation/' +  group + "/"  + file_name.replace('.json','.html')
                    item_description = SubElement(rss_item, 'description')
                    description_text = html.escape(meta_info)
                    item_description.text = description_text
                    
                    image_url = f"https://www.ransomware.live/ransomwarelive.png"
                    image_path = f"./docs/ransomwarelive.png"  # Path to the image file
                    image_size = os.path.getsize(image_path)  # Get file size in bytes
                    enclosure = SubElement(rss_item, 'enclosure')
                    enclosure.set('url', image_url)
                    enclosure.set('type', 'image/png')
                    enclosure.set('length', str(image_size))  # Set the image length attribute

                    item_guid = SubElement(rss_item, 'guid')
                    item_guid.text = 'https://www.ransomware.live/#/negotiation/' + str(group) + "/" + str(file_name)  + '?' +md5GUID(file_path)
    
                    date_rfc822 = datetime.strptime(modified_date, '%Y-%m-%dT%H:%M:%S.%f').strftime('%a, %d %b %Y %H:%M:%S +0000')
    
                    item_pubdate = SubElement(rss_item, 'pubDate')
                    item_pubdate.text = date_rfc822

    # Convertissez l'objet rss en chaîne de caractères et enregistrez-le dans un fichier
    rss_str = tostring(rss, encoding='unicode')
    with open('./docs/negotiations.xml', 'w') as f:
        f.write(rss_str)
    stdlog('Negotiations Feed : ' + 'generated')



def generate_rss_feed():
    generate_victims_feed()
    generate_cyberattacks_feed()
    generare_nego_feed() 