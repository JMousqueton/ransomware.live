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

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('metaencryptor-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card-header')
                for card in cards:
                   for card in cards:
                    victim = card.get_text(strip=True)
                    description = card.find_next('p', class_='card-text').get_text(strip=True)
                    
                    website_link = card.find_next('a', class_='btn btn-secondary btn-sm')
                    website = website_link['href'] if website_link else None
                    
                    post_link = card.find_next('a', class_='btn btn-primary btn-sm')
                    if post_link:
                        #post_url = "https://metacrptmytukkj7ajwjovdpjqzd7esg5v3sg344uzhigagpezcqlpyd.onion" + post_link['href']
                        post_url = find_slug_by_md5('metaencryptor', extract_md5_from_filename(str(html_doc))) +  post_link['href']
                    else:
                        post_url =  None
                    appender(victim, 'metaencryptor', description, website, '', post_url)
                file.close()
        except Exception as e:
            errlog('metaencryptor - parsing fail with error: ' + str(e))
