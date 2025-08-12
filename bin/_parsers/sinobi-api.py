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
from shared_utils import appender, errlog, stdlog


env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))
db_dir = Path(home + os.getenv("DB_DIR"))


# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}
def get_fqdns_from_json(filename, group_name):
    # Load the JSON data from the file
    with open(filename, 'r') as file:
        data = json.load(file)

    # Initialize a list to hold the FQDNs
    fqdns = []

    # Loop through each item in the JSON data (assuming top level is a list)
    for item in data:
        # Check if the group name matches
        if item.get("name") == group_name:
            # Loop through each location in the locations list
            for location in item.get("locations", []):
                # Append the FQDN to the list
                fqdns.append(location["fqdn"])
            break

    return fqdns


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

def convert_datetime(date_str):
    # Parse the ISO 8601 formatted string to a datetime object
    dt = datetime.fromtimestamp(date_str / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

def main():
    filename = db_dir / 'groups.json'
    group_name = "sinobi"
    fqdns = get_fqdns_from_json(filename, group_name)   
    for fqdn in fqdns:
        try:
            #onion_url= 'http://sinobi6ftrg27d6g4sjdt65malds6cfptlnjyw52rskakqjda6uvb7yd.onion/api/v1/blog/get/announcements'
            onion_url = 'http://' + fqdn + '/api/v1/blog/get/announcements'
            #stdlog('Fetching :'+onion_url) 
            json_data = fetch_json_from_onion_url(onion_url)
            #stdlog(onion_url+" Fetched")
            if json_data is not None:
                for item in json_data['payload']['announcements']:
                    id = item['_id']
                    victim = unquote(item['company']['company_name'])
                    country = item['company']['country']
                    description = unquote(item['description'][0])
                    date_created = convert_datetime(item['createdAt'])
                    link = 'http://' + fqdn + '/leaks/' + str(id) 
                    appender(victim,'sinobi',description,None,date_created,link)
        except Exception as e:
           stdlog('Sinobi - parsing fail with error: ' + str(e) + 'with ' + fqdn)