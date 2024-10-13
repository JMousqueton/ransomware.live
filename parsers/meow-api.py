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
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import urllib3
from dotenv import load_dotenv 
env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

DATA_DIR = os.getenv('DATA_DIR')
GROUPS_FILE = os.getenv('GROUPS_FILE')


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
    dt = datetime.fromisoformat(date_str.rstrip('Z'))
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

def main():

    filename = DATA_DIR +  GROUPS_FILE
    group_name = "meow"
    fqdns = get_fqdns_from_json(filename, group_name)   
    for fqdn in fqdns:
        try:
            #onion_url= 'http://meow6xanhzfci2gbkn3lmbqq7xjjufskkdfocqdngt3ltvzgqpsg5mid.onion/backend/post/getPosts'
            onion_url = 'http://' + fqdn + '/backend/post/getPosts'
            #stdlog('Fetching :'+onion_url) 
            json_data = fetch_json_from_onion_url(onion_url)
            #stdlog(onion_url+" Fetched")
            if json_data is not None:
                for item in json_data['data']:
                    id = item['id']
                    title = item['title'].strip()
                    description = item['description']
                    date_created = convert_datetime(item['createdAt'])
                    link = 'http://' + fqdn + '/product/' + str(id) 
                    appender(title,'meow',description,'',date_created,link)
        except Exception as e:
           stdlog('Medusa - parsing fail with error: ' + str(e))