"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import socks
import json
import urllib3
## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender, openjson



onion_url= 'http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion/api/guest/blog/posts?page=1'

# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

# Function to convert date format
def convert_date_format(date_str):
    # Parse the original date string to a datetime object
    original_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    datetime_obj = datetime.strptime(date_str, original_format)
    # Convert the datetime object to the desired string format
    new_format = "%Y-%m-%d %H:%M:%S.%f"
    return datetime_obj.strftime(new_format)

def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies,verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    return json_data

def main():
    try:
        json_data = fetch_json_from_onion_url(onion_url)

        if json_data is not None:
            for item in json_data:
                if 'data' in json_data and 'publications' in json_data['data'] and json_data['data']['publications']:
                    publications = json_data['data']['publications']
                    for publication in publications:
                        publication_date = convert_date_format(publication['created_at'])
                        victim = publication['name']
                        website = publication['site']
                        description = publication['description']
                        appender(victim, 'dragonforce',description,website,publication_date,'')

    except Exception as e:
        errlog(group_name + ' - parsing fail with error: ' + str(e))