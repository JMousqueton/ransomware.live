"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys, re
from datetime import datetime
import requests
import socks
import json
import urllib3
from urllib.parse import urlparse

#env_path = Path("../.env")
#load_dotenv(dotenv_path=env_path)
#home = os.getenv("RANSOMWARELIVE_HOME")
#tmp_dir = Path(home + os.getenv("TMP_DIR"))

from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog, openjson


onion_url= 'http://izsp6ipui4ctgxfugbgtu65kzefrucltyfpbxplmfybl5swiadpljmyd.onion/intrumpwetrust/api/posts?page=1&perPage=15'

# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}


def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies,verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        errlog("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    #json_data = openjson('/tmp/dragon.json')
    return json_data

        
def extract_website(first_line):
    """Extract a website URL from the first line of text if present."""
    match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', first_line)
    return match.group(0) if match else ""

def transform_date(date_str):
    """Transform the date to %Y-%m-%d %H:%M:%S.%f format."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))  # Handle ISO8601 format
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return "Invalid date"

def extract_fqdn(website_url):
    """Extract the FQDN (Fully Qualified Domain Name) from the URL."""
    if website_url.startswith("www."):
        website_url = "http://" + website_url  # Add scheme to parse "www." URLs
    parsed_url = urlparse(website_url)
    return parsed_url.netloc if parsed_url.netloc else ""

def main():
    try:
        data = fetch_json_from_onion_url(onion_url)
        for item in data.get('items', []):
            victim = item.get('title', 'Unknown Victim')
            text = item.get('text', '')
            date = item.get('date', 'No date provided')
            publication_date = transform_date(date)
            description = text[:200]
            first_line = text.splitlines()[0] if text else ''
            website = extract_website(first_line)
            website = extract_fqdn(website)
        
            appender(victim, 'morpheus',description,website,publication_date)
    except Exception as e:
        errlog('morpheus' + ' - parsing fail with error: ' + str(e))

        