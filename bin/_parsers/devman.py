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
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, stdlog, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('devman-'):
                html_doc=tmp_dir /  filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                rows = soup.find_all('table')[0].find_all('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    victim = cols[0].get_text(strip=True)
                    victim =  re.sub(r'\([^)]*\)', '', victim)
                    ransom = cols[1].get_text(strip=True)
                    status = cols[2].get_text(strip=True)
                    extra_infos = { 'ransom': ransom }
                    
                    appender(victim, 'devman',status,"","","",'',extra_infos)
                file.close()
        except Exception as e:
            errlog('devman' + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
