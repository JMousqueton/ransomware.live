import os, sys
import urllib3
import requests
import json
import pycountry
from datetime import datetime
from shared_utils import appender
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

onion_url = 'http://j5o5y2feotmhvr7cbcp2j2ewayv5mn5zenl3joqwx67gtfchhezjznad.onion/api/data?page=1'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

headers = {
    "Host": "j5o5y2feotmhvr7cbcp2j2ewayv5mn5zenl3joqwx67gtfchhezjznad.onion",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "http://j5o5y2feotmhvr7cbcp2j2ewayv5mn5zenl3joqwx67gtfchhezjznad.onion/",
    "Connection": "keep-alive",
    #"If-None-Match": 'W/"ce2-l4dUcvpqzE7te+sHecTbsdO7Gsk"',
    "Priority": "u=4"
}

def fetch_json_from_onion_url(url):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=30)
        #print(f"Status code: {response.status_code}")
        #print(f"Response headers: {response.headers}")
        #print(f"Raw response text (first 500 chars):\n{response.text[:500]}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def convert_country_to_code(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except LookupError:
        return ""  # Unknown

def main():
    json_data = fetch_json_from_onion_url(onion_url)
    if json_data and "items" in json_data:
        for item in json_data["items"]:
            company = item.get('company', '').strip()
            domain = item.get('domain', '').strip()
            size = item.get('size', '').strip()
            comment = item.get('comment', '').strip()
            country = item.get('country', '').strip()
            published = item.get('time', '')[:10]  # format: YYYY-MM-DD
            country_code = convert_country_to_code(country) if country else item.get('code', '')
            
            extra_infos = {
                'size': size
            }

            print(f"[+] {company} ({domain}) - {country_code} - {published}")
            appender(company, 'crypto24', comment, domain, published, '', country_code, extra_infos)

if __name__ == "__main__":
    main()
