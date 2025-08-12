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
from datetime import datetime
import requests
import socks
import json
import urllib3

#env_path = Path("../.env")
#load_dotenv(dotenv_path=env_path)
#home = os.getenv("RANSOMWARELIVE_HOME")
#tmp_dir = Path(home + os.getenv("TMP_DIR"))

from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog, openjson


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
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    #json_data = response.json()
    #json_data = openjson('/tmp/dragon.json')
    #return json_data

def main():
    try:
        json_data = fetch_json_from_onion_url(onion_url)

        if json_data and 'data' in json_data and 'publications' in json_data['data']:
            publications = json_data['data']['publications']
            for publication in publications:
                publication_date = convert_date_format(publication['created_at'])
                victim = publication['name']
                website = publication.get('website', '')
                description = publication.get('description', '')
                uuid = publication.get('uuid', '')
                link = f"http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion/blog/?post_uuid={uuid}"
                appender(victim, 'dragonforce', description, website, publication_date, link)

    except Exception as e:
        errlog('dragonforce - parsing fail with error: ' + str(e))
