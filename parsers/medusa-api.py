"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import unquote
import requests
import socks
import json
## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender,openjson, openjson


# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies,verify=False, timeout=30)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        errlog(f"Error: " + str(e))
        return None
    # Parse and return the JSON data
    try:
        json_data = response.json()
        return json_data
    except ValueError as e:
        errlog(f"Error parsing JSON: " + str(e))
        return None


def main():
    json_onion_url= 'http://cx5u7zxbvrfyoj6ughw76oa264ucuuizmmzypwum6ear7pct4yc723qd.onion/api/search?company=&page=0'
    site_onion_url= 'http://cx5u7zxbvrfyoj6ughw76oa264ucuuizmmzypwum6ear7pct4yc723qd.onion/detail?id='

    # json_data = fetch_json_from_onduion_url(json_onion_url)
    try:
        json_data = openjson('/tmp/medusa.json')
        if json_data is not None:
            for item in json_data['list']:
                victim = item['company_name']
                id = item['id']
                description = item['description']
                updated_date = item['updated_date']+'.000000'
                post_url = site_onion_url + id 
                appender(victim,'medusa',description,'',updated_date,post_url)
    except Exception as e:
           stdlog('Medusa - parsing fail with error: ' + str(e))
    
