import xml.etree.ElementTree as ET
import requests
from io import StringIO
from datetime import datetime
from sharedutils import stdlog, dbglog, errlog   # , honk
from parse import appender
import re


# Set up Tor SOCKS proxy
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

onion_url = "http://3ytm3d25hfzvbylkxiwyqmpvzys5of7l4pbosm7ol7czlkplgukjq6yd.onion/atom.xml"

def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def convert_pubdate_format(pub_date_str):
    try:
        # Adjusting the format to parse the milliseconds ('.%f') and 'Z' (UTC)
        if pub_date_str.endswith('Z'):
            pub_date_str = pub_date_str[:-1] + '+0000'  # Replace 'Z' with UTC offset
        date_object = datetime.strptime(pub_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        # Convert to the desired format without timezone information
        return date_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Removing last three digits of microseconds for '.000'
    except ValueError:
        return None



def main():
    try:
        response = requests.get(onion_url, proxies=proxies, verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        # Log the error message
        print(f"Error: {e}")
        return
    xml_file = StringIO(response.text)

    # Parse the XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Correct namespace handling for Atom feeds
    ns = {'default': 'http://www.w3.org/2005/Atom'}

    # Extracting and printing the title and link of each item
    for entry in root.findall('default:entry', ns):
        title = entry.find('default:title', ns).text
        link = entry.find('default:link', ns).attrib['href']
        pubdate = convert_pubdate_format(entry.find('default:updated', ns).text)
        description = remove_html_tags(entry.find('default:summary', ns).text)
        """
        Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
        """
        appender(title, 'slug', description.replace('\n',' '),'',pubdate,link)   

if __name__ == "__main__":
    main()
