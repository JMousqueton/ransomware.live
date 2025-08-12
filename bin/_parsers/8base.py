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
            if filename.startswith('8base-'):
                html_doc=tmp_dir /  filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', class_='list-group-item')
                for div in divs_name:
                    link = div.find('a')['href']
                    name = div.find('a').text.strip()
                    tmp = div.find('div', class_='d-flex gap-2 small mt-1 opacity-25').text.strip()
                    date_string = tmp.splitlines()[0].replace("Downloaded: ","")
                    try: 
                        published = datetime.strptime(date_string, "%d.%m.%Y").strftime("%Y-%m-%d %H:%M:%S.%f")
                    except: 
                        published = datetime.strptime(date_string, "%d.%m.%y").strftime("%Y-%m-%d %H:%M:%S.%f")
                    description = div.find('div', class_='small opacity-50').text.strip()
                    appender(
                        victim=name,
                        group_name='8base',
                        description=description,
                        website="",  # Optional, leave empty or populate if relevant data exists
                        published=published,
                        post_url=link,
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog('8base - parsing fail with error: ' + str(e) + 'in file:' + filename) 
