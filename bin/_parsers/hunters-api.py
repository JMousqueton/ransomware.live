"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys
#from bs4 import BeautifulSoup
import urllib3
import requests
import socks
import json
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))



onion_url= 'https://hunters55rdxciehoqzwv7vgyv6nt37tbwax2reroyzxhou7my5ejyid.onion/api/public/companies'

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
        print("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    return json_data

def convert_date(unix_timestamp):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(unix_timestamp)
    # Format the datetime object as a string with microseconds
    formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime

def convert_text(txt):
    if txt == True:
        return "yes"
    else:
        return "no"

def main():
    #stdlog('Fetching :'+onion_url) 
    json_data = fetch_json_from_onion_url(onion_url)
    #stdlog(onion_url+" Fetched")
    if json_data is not None:
        for item in json_data:
          #try:
            id = item['id']
            title = item['title'].strip()
            country_code = item['country']
            # country = get_country(item['country'])
            website = item.get('website','')
            exfiltration = item['exfiltrated_data']
            encryption = item['encrypted_data']
            published = item.get('updated_at','')
            description = "Exfiltraded data : " + convert_text(exfiltration) +  " - Encrypted data : " + convert_text(encryption)
            post_url = "https://hunters55rdxciehoqzwv7vgyv6nt37tbwax2reroyzxhou7my5ejyid.onion/companies/" + id 
            if not website:
                website=''
            if country_code: 
                country_code = country_code.upper()
            else:
                country_code = '' 
            """
                def appender(post_title, group_name, description="", website="", published="", post_url=""):
            """
            appender(title, 'hunters', description,website, convert_date(published),post_url,country_code)
          #except:
          #    stdlog('Hunters API error : ' + title)
