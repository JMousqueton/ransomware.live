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
            if filename.startswith('bianlian-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('section', {"class": "list-item"})
                for div in divs_name:
                    title = div.h1.text.strip()
                    post = div.find('a', {'class': 'readmore'})
                    post = post.get('href')
                    try:
                        url = find_slug_by_md5('bianlian', extract_md5_from_filename(str(html_doc))) + str(post)
                    except:
                        #url = ''
                        url = "bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion" + str(post)
                    description = div.div.text.strip()
                    description = description.replace('%20',' ')
                    appender(title, 'bianlian', description,"","",url)
                file.close()
        except Exception as e:
            errlog('bianlian - parsing fail with error: ' + str(e) + 'in file:' + filename)
