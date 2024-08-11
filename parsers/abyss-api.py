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
import requests
import datetime
import json

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender




# Tor proxy settings
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Group name you're interested in
target_group_name = "abyss"


def main():
    # Read the groups.json file
    with open('./data/groups.json', 'r') as file:
        groups_data = json.load(file)

    # Find the specific group by name
    group = next((g for g in groups_data if g.get('name') == target_group_name), None)

    locations = group.get('locations', [])
        
    for location in locations:
        slug = location.get('slug')
        if slug:
            slug = f'{slug}static/data.js'
            stdlog(f"Requesting data from: {slug}") 
                
            # Make the request via Tor
            response = requests.get(slug, proxies=proxies)
                
            if response.status_code == 200:
                data_js_content = response.text

                # Extract the relevant array data manually
                data_js_content = data_js_content.strip()
                # Remove 'let data =' and the trailing semicolon
                if data_js_content.startswith("let data ="):
                    data_js_content = data_js_content[len("let data ="):].strip()

                try:
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
                    errlog(f"Failed to evaluate the data: {e}")
            else:
                errlog(f"Failed to fetch the file from {slug}. HTTP Status Code: {response.status_code}")