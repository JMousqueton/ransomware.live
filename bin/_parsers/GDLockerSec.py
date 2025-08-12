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


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('GDLockerSec-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    parent_anchor = card.find_parent('a')  # Find the parent <a> tag
                    link = parent_anchor['href'] if parent_anchor else None
                    title = card.find('div', class_='card-title').text.strip() if card.find('div', class_='card-title') else None
                    title =  title.split("|")[0]
                    countdown_date = card.find('strong', class_='countdown-date').text.strip() if card.find('strong', class_='countdown-date') else None
                    visits = card.find(string=lambda text: 'Visits:' in text)
                    visits = visits.split(':')[1].strip() if visits else None
                    data_size = card.find(string=lambda text: 'Data Size:' in text)
                    data_size = data_size.split(':')[1].strip() if data_size else None
                    last_view = card.find(string=lambda text: 'Last View:' in text)
                    last_view = last_view.split(':')[1].strip() if last_view else None
                    footer_timestamp = card.find_next('div', class_='card-footer').text.strip() + ".000000" if card.find_next('div', class_='card-footer') else None
                    appender(
                        victim=title,
                        group_name='GDLockerSec',
                        description=data_size,
                        website='',  # Optional, leave empty or populate if relevant data exists
                        published=footer_timestamp,
                        post_url=link,
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog('GDLockerSec - parsing fail with error: ' + str(e) + 'in file:' + filename) 
