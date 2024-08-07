import json
from datetime import datetime
import hashlib,os
import uuid
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import html  # Import the html module
import xml.sax.saxutils as saxutils
import sys

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog

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

# Chargez les données du fichier JSON
directory_path = '/var/www/ransomware-ng/data/'



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


