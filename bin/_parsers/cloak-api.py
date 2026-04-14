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
import requests

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
            # URL of the JSON data
            url = 'https://www.ransomlook.io/export/2'
            
            # Tor proxy configuration
            proxies = {
                    'http': 'socks5h://127.0.0.1:9050',
                    'https': 'socks5h://127.0.0.1:9050'
            }
            try:
                
                # Fetch data from the URL via Tor proxy
                response = requests.get(url, proxies=proxies, timeout=30)
                response.raise_for_status()  # Raise an error for bad status codes
                data = response.json()

                # Define the ransomware group name
                group_name = "cloak"

                # Extract and transform data for the specified ransomware group
                group_data = data.get(group_name, [])

                for entry in group_data:
                    post_title = entry.get("post_title", "")
                    description = entry.get("description", "N/A")
                    #print(f"Name: {post_title}")
                    #print(f"Desc.: {description}")
                    appender(post_title,group_name,description)
                    """
                    +------------------------------+------------------+----------
                    | Description | Published Date | Victim's Website | Post URL |
                    +------------------------------+------------------+----------+
                    |      X      |      X         |                 |     x    |
                    +------------------------------+------------------+----------+
                    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
                    """
            except Exception as e:
                errlog(group_name + ' - parsing fail with error: ' + str(e))

