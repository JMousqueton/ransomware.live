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
    pattern = r"^(FILES PART [1-9]|COMPANY's PART[1-9]|PART [1-9]|HOME|HOW TO DOWNLOAD\?|ARCHIVE|ARCHIVE[1-9]|ARCHIVE[10-99])$"

    blacklist=['HOME', 'HOW TO DOWNLOAD?', 'ARCHIVE']
    for filename in os.listdir(tmp_dir):
        if filename.startswith('clop-'):
            html_doc= tmp_dir / filename
            file=open(html_doc,'r')
            soup=BeautifulSoup(file,'html.parser')
            ###divs_name=soup.find_all('span', {"class": "g-menu-item-title"})
            menu_items = soup.select(".g-menu-item")
            ##for div in divs_name:
            for item in menu_items:
                ### for item in div.contents:
                ###    victim = item.text.strip()
                title_tag = item.select_one(".g-menu-item-title")
                victim = title_tag.text.strip()
                link_tag = item.select_one(".g-menu-item-container")
                link = link_tag["href"].strip()
                post_url = find_slug_by_md5('clop', extract_md5_from_filename(str(html_doc))) + str(link)
                if not re.match(pattern, victim):
                    appender(victim, 'clop','','','',post_url)
                    