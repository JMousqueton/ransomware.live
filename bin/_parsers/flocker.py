"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,json, re
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
            if filename.startswith('flocker-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                entries = soup.find_all('h2', class_='entry-title ast-blog-single-element')
                for entry in entries:
                    victim_name = entry.text.strip()
                    link = entry.find('a')['href']
                    parent_div = entry.find_parent('article')
                    date_span = parent_div.find('span', itemprop='datePublished')
                    if date_span:
                        date = date_span.text.strip()
                        parsed_date = datetime.strptime(date, '%B %d, %Y')
                        date = parsed_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                        date = ''
                    description = entry.find_next_sibling('div', class_='ast-excerpt-container ast-blog-single-element').text.strip()
                    appender(victim_name,'flocker',description,'',date,link)
        except Exception as e:
            errlog('Flocker - parsing fail with error: ' + str(e) + 'in file:' + filename)