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
from datetime import timedelta

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('stormous-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                company_posts = soup.find_all('div', class_='post-card')
                for post in company_posts:
                    date = post.find('div', class_='date').get_text(strip=True) if post.find('div', class_='date') else ''
                    company_name = post.find('h4').get_text(strip=True) if post.find('h4') else 'N/A'
                    description = post.find('p', class_='subtitle').get_text(strip=True) if post.find('p', class_='subtitle') else ''
                    size = post.find('p', class_='size').get_text(strip=True) if post.find('p', class_='size') else ''
                    if size:
                        extra_infos = { 'data_size': size }
                    else:
                        extra_infos = {}
                    url_tag = post.find('a', class_='read-more')
                    if url_tag:
                        post_url = url_tag['href'] if url_tag else 'N/A'
                    else:
                       post_url = '' 
                    appender(company_name, 'stormous', description, "", "", post_url, "", extra_infos)
                file.close()
        except Exception as e:
            errlog('Stormous - parsing fail with error: ' + str(e) + 'in file:' + filename) 
