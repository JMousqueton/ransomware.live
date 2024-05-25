import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import hashlib,os
from sharedutils import stdlog

def md5GUID(input_string):
    md5_hash = hashlib.md5(input_string.encode('utf-8')).hexdigest()
    return md5_hash

print(
    '''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \     ransomwhat?      /  ************  \ 
    --------------------                    --------------------
    '''
)

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
    rss = ET.Element('rss', {'version': '2.0', 'xmlns:atom': 'http://www.w3.org/2005/Atom'})
    channel = ET.SubElement(rss, 'channel')

    # Add Channel title
    title = ET.SubElement(channel, 'title')
    title.text = "Ransomware.live: Last Cyber attacks Feed"

    # Add Channel link
    link = ET.SubElement(channel, 'link')
    link.text = "https://www.ransomware.live/#/recentcyberattacks"

    # Add Channel description
    description = ET.SubElement(channel, 'description')
    description.text = "Last 100 cyber attacks monitoring by Ransomware.live"
  
    # Add Channel image
    image = ET.SubElement(channel, 'image')
    image_url = "https://www.ransomware.live/ransomwarelive.png"
    ET.SubElement(image, 'url').text = image_url
    ET.SubElement(image, 'title').text = "Ransomware.live: Last Cyber attacks Feed"
    ET.SubElement(image, 'link').text = "https://www.ransomware.live/#/recentcyberattacks"

    # Add atom:link element
    atom_link = ET.SubElement(channel, 'atom:link', href='https://www.ransomware.live/cyberattacks.xml', rel='self', type='application/rss+xml')

    # Add RSS elements for each sorted item
    for item in sorted_data:
        rss_item = ET.SubElement(channel, 'item')
        ET.SubElement(rss_item, 'title').text = item['title'] + ' ('+ item['country'] + ')'
        ET.SubElement(rss_item, 'description').text = '(' + item['domain'] + ') ' + item['summary']
        ET.SubElement(rss_item, 'link').text = 'https://www.ransomware.live/redirect.html?url=' + item['url']

        # Convert date to RFC-822 format with GMT timezone
        date_str = item['date']
        datetime_obj = datetime.strptime(date_str, '%Y-%m-%d')
        datetime_obj = pytz.utc.localize(datetime_obj)  # Set the timezone to GMT
        rfc_822_date = datetime_obj.strftime('%a, %d %b %Y %H:%M:%S %z')
        ET.SubElement(rss_item, 'pubDate').text = rfc_822_date

        # Calculate MD5 hash of the link
        link_md5 = hashlib.md5(item['url'].encode()).hexdigest()
        image_path = os.path.join(image_directory, f"{link_md5}.png")

        # Check if the image exists for the item
        if os.path.exists(image_path):
            item_image_url = f"https://www.ransomware.live/screenshots/news/{link_md5}.png"
            image_size = os.path.getsize(image_path)
            ET.SubElement(rss_item, 'enclosure', attrib={
                          'url': item_image_url, 'type': 'image/png', 'length': str(image_size)})

        item_guid = ET.SubElement(rss_item, 'guid')
        item_guid.text = 'https://www.ransomware.live/?=' +md5GUID(item['title'])

    # Create an ElementTree object and write to the file in ./docs directory
    file_path = './docs/cyberattacks.xml'
    tree = ET.ElementTree(rss)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)
    stdlog('Cyber attacks Feed : ' + 'generated')
else:
    stdlog("Failed to fetch data:", response.status_code)
