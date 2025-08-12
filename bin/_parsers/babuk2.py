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
            if filename.startswith('babuk2-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', class_='col-lg-4 col-sm-6 mb-4')
                for div in divs_name:
                    title = div.find('h5').text.strip()
                    publication_date = div.find('div', class_='published').text.strip() +  '.000000'
                    description = div.find('div', class_='col-12').text.strip()
                    link = find_slug_by_md5('babuk2', extract_md5_from_filename(str(html_doc))) + div.find('a')['href']
                    link = link.replace('//','/')
                    appender(title, 'babuk2',description,'',publication_date,link)
                file.close()
        except Exception as e:
            errlog('Babuk - parsing fail with error: ' + str(e) + 'in file:' + filename) 

