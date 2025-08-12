"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re, json
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
            if filename.startswith('blacksuit-'):
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs=soup.find_all('div', {"class": "card"})
                for article in divs:
                    # Extract the title
                    title = article.find('div', class_='title').text.strip()
                    title = title.replace('amp;','')
                    # Extract the URL
                    url_site = find_slug_by_md5('blacksuit', extract_md5_from_filename(str(html_doc)))
                    #url_site = "weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd"
                    url = article.find('div', class_='title').a['href']
                    post_url = url_site + '/' +  url

                    try:
                        website= article.find('div', class_='url').a['href']
                    except:
                        website=''
                    try:
                        description = article.find('p').text.strip().replace('\n', ' ')
                    except:
                        description = ''
                    appender(title, 'blacksuit', description,website,'',post_url)

                file.close()
        except:
            errlog('blacksuit : ' + 'parsing fail')
