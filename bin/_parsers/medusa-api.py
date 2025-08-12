"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,json
#from bs4 import BeautifulSoup
from datetime import datetime
import requests
import urllib3
from urllib.parse import unquote
from dotenv import load_dotenv 
from pathlib import Path
from shared_utils import appender, errlog, stdlog, openjson


env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))
db_dir = Path(home + os.getenv("DB_DIR"))


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
    site_onion_url= 'http://xfv4jzckytb4g3ckwemcny3ihv4i5p4lqzdpi624cxisu35my5fwi5qd.onion/detail?id='

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
                ransom = item['price_download']
                extra_infos = { 'ransom': ransom }
                appender(victim,'medusa',description,'',updated_date,post_url,'',extra_infos)
    except Exception as e:
           stdlog('Medusa - parsing fail with error: ' + str(e))
    
