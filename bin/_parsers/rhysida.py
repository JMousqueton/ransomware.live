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
            if filename.startswith('rhysida-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                div_containers = soup.find_all('div', class_='border m-2 p-2')
                for div in div_containers:
                    title_div = div.find('div', class_='m-2 h4')
                    title = title_div.text.strip() if title_div else ''
                    description_div = div.find('div', class_='m-2')
                    description = description_div.text.strip().replace('\n',' ') if description_div else ''
                    post_url=''
                    try:
                        post_url = 'archive.php?company=' + div.find('button')['data-company']
                        post_url = find_slug_by_md5('rhysida', extract_md5_from_filename(str(html_doc))).replace('/archive.php?auction','') + '/' + post_url
                    except:
                        post_url =''
                    if len(title) != 0: 
                        appender(title, 'rhysida', description,"","",post_url)
                file.close()
        except Exception as e:
            errlog('Rhysida - parsing fail with error: ' + str(e) + 'in file:' + filename) 

