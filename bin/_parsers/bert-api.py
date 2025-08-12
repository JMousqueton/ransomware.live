import os, sys, re
import urllib3
import requests
import json
from datetime import datetime
from shared_utils import appender
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

onion_url = 'http://hahahasrzrdb6bbg6aoxbgd47fxd4icuvucncmeldsjgnvdzoze2egid.onion/api/publications/s'

# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
    return response.json()

def convert_date(unix_timestamp=None):
    if not unix_timestamp:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    dt = datetime.fromtimestamp(unix_timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

def main():
    json_data = fetch_json_from_onion_url(onion_url)
    if json_data and isinstance(json_data, list):
        for item in json_data:
            title = item.get('title', '').strip()
            title = re.sub(r"\s*\(UPDATE \d{1,2}/\d{1,2}/\d{4}\)", "", title)
            description = item.get('short_desc', '')
            date = item.get('createdAt', '')
            dt = datetime.fromisoformat(date.replace("Z", "+00:00")) 
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            post_url = "http://bertblogsoqmm4ow7nqyh5ik7etsmefdbf25stauecytvwy7tkgizhad.onion/post/" + item.get('id', '')
            appender(title, 'bert', description, '', formatted_timestamp, post_url)

if __name__ == "__main__":
    main()
