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
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename,errlog
from pathlib import Path
from dotenv import load_dotenv

import requests
import datetime
import json


env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
db_dir = Path(home + os.getenv("DB_DIR"))

# Tor proxy settings
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Group name you're interested in
target_group_name = "abyss"


def main():
    # Read the groups.json file
    with open(f'{db_dir}/groups.json', 'r') as file:
        groups_data = json.load(file)

    # Find the specific group by name
    group = next((g for g in groups_data if g.get('name') == target_group_name), None)

    locations = group.get('locations', [])
        
    for location in locations:
        slug = location.get('slug')
        if slug:
            slug = f'{slug}static/data.js'
            #print(f"Requesting data from: {slug}") 
                
            # Make the request via Tor
            try: 
                response = requests.get(slug, proxies=proxies, timeout=(60, 60))
                
                if response.status_code == 200:
                    data_js_content = response.text

                    # Extract the relevant array data manually
                    data_js_content = data_js_content.strip()
                    # Remove 'let data =' and the trailing semicolon
                    if data_js_content.startswith("let data ="):
                        data_js_content = data_js_content[len("let data ="):].strip()

                        data = eval(data_js_content)

                        # Process the data
                        for item in data:
                            victim = item.get('title', 'No title')
                            full_lines = item.get('full', '').split('<br>')

                            if len(full_lines) > 1:
                                description = full_lines[1].strip()
                            else:
                                description = ""

                            appender(victim, 'abyss', description) 

            except Exception as e:
                    errlog(f"Abyss : Failed to evaluate the data: {e}")
        else:
             errlog(f"Abyss : Failed to fetch the file from {slug}. HTTP Status Code: {response.status_code}")
