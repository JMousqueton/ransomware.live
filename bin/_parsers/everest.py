"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,json
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
            if filename.startswith('everest-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for div in soup.find_all('div', class_='category-item js-open-chat'):
                    # Victim name
                    title_tag = div.find('div', class_='category-title')
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    # Published date
                    date_tag = div.find('div', class_='category-date')
                    published = ''
                    if date_tag:
                        date_str = date_tag.get_text(strip=True)
                        try:
                            # Try to parse date in format like '26 apr 2025'
                            published_dt = datetime.strptime(date_str, '%d %b %Y')
                            published = published_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
                        except Exception:
                            published = ''
                    url = div.get('data-translit')
                    # TODO: get base url from the groups.json for better maintainability
                    url = find_slug_by_md5('everest', extract_md5_from_filename(str(html_doc))) + "news/" + url
   
                    if title != "Total Patient Care LLC;A Sensitive Touch Home Health;Alphastar Home Health Care;Heart of Texas Home Healthcare Services Inc Data Leak":
                        appender(title, 'everest', '', '', published, url)
                    else:
                        print('Everest - Skipping title: ' + title)
                file.close()
        except Exception as e:
            errlog("Everest" + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)

