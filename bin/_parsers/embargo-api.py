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
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))
db_dir = Path(home + os.getenv("DB_DIR"))


import requests
import urllib3
import json


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
        response = requests.get(onion_url, proxies=proxies, verify=False)
        response.raise_for_status()
        return json.loads(response.text)  # ✅ parsing manuel
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        return None

def convert_datetime(iso_datetime):
    # Parse the ISO 8601 formatted string to a datetime object
    if '+' in iso_datetime:
        iso_datetime = iso_datetime.split('+')[0]
        return iso_datetime
    else:
        dt_obj = datetime.fromisoformat(iso_datetime)
    
        # Format the datetime object to the desired string format
        formatted_datetime = dt_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
    
        return formatted_datetime

def main():
    filename = db_dir / "groups.json"
    group_name = "embargo"
    fqdns = get_fqdns_from_json(filename, group_name)

    for fqdn in fqdns:
        onion_url = f"http://{fqdn}/api/blog/get"
        json_data = fetch_json_from_onion_url(onion_url)

        if json_data is None:
            errlog(f"Failed to fetch data from {onion_url}")
            continue

        blogs = json_data.get("blogs", [])
        if not isinstance(blogs, list):
            errlog(f"Unexpected structure in response from {onion_url}: 'blogs' is not a list")
            continue

        for item in blogs:
            try:
                post_id = item['_id']
                title = item.get('comname', '').strip()
                description = item.get('descr', '')
                comments = item.get('comments', '')
                date_created = item.get('date_created', '').replace('T', ' ')
                pubdate = convert_datetime(date_created)
                post_url = f"http://{fqdn}/#/post/{post_id}"

                appender(title, group_name, f"{description} - {comments}", "", pubdate, post_url)
            except Exception as e:
                errlog(f"Error parsing item from {onion_url}: {e}")
