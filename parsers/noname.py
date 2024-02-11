import xml.etree.ElementTree as ET
import requests
from io import StringIO
from datetime import datetime
from sharedutils import stdlog, dbglog, errlog   # , honk
from parse import appender


# Set up Tor SOCKS proxy
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

# Replace this with the actual onion URL
onion_url = "http://noname2j6zkgnt7ftxsjju5tfd3s45s4i3egq5bqtl72kgum4ldc6qyd.onion/wp/feed"

def convert_pubdate_format(pub_date_str):
    # Parse the original date format
    try:
        date_object = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
        # Convert to the desired format
        return date_object.strftime('%Y-%m-%d %H:%M:%S.%f')
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

    # Extracting and printing the title and link of each item
    for item in root.findall('.//item'):
        title = item.find('title').text
        if title == '[NEGOTIATED]':
            continue
        link = item.find('link').text
        pubdate = convert_pubdate_format(item.find('pubDate').text)
        description = item.find('description').text
        """
        Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
        """
        appender(title, 'noname', description.replace('\n',' '),'',pubdate,link)

        
   

if __name__ == "__main__":
    main()
