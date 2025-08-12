"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import requests

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


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
        stdlog("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    return json_data


def main():
    json_onion_url= 'http://termitelfvhutinrgpe55siktisskbqntkuq7ojidg42zh26avekq6qd.onion/api/blog/blogs'
    site_onion_url= 'http://termiteuslbumdge2zmfmfcsrvmvsfe4gvyudc5j6cdnisnhtftvokid.onion/post'


    try:
        json_data = fetch_json_from_onion_url(json_onion_url)
        #json_data = openjson('/tmp/incransom.json')


    except:
        json_data = None
        errlog('No Data in json')
    if json_data is not None:
        #print(json_data)
        for victim in json_data:
            title = victim.get('title', 'N/A')
            website = victim.get('address', 'N/A')
            description = victim.get('description', 'N/A')
            original_date = victim.get('publishDate', 'N/A')
            victim_id = victim.get('_id', 'N/A')


            try:
                # Parse original date and convert to the desired format
                dt = datetime.strptime(original_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                formatted_date = ''

            post_url = site_onion_url+'/'+ victim_id

            appender(title,'termite',description,website,formatted_date,post_url)
    
