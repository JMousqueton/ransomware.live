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
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog, stdlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('apt73-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                stdlog(f'Parsing: {html_doc}')
                soup = BeautifulSoup(file, 'html.parser')
                segment_box = soup.find('div', class_='segment__box')
                for segment in segment_box.find_all('div', class_='segment'):
                    link = segment.get('onclick').split("'")[1] if segment.get('onclick') else None
                    victim = segment.find('div', class_='segment__text__off').text.strip() if segment.find('div', class_='segment__text__off') else None
                    post_url = 'http://basherq53eniermxovo3bkduw5qqq5bkqcml3qictfmamgvmzovykyqd.onion' +  str(link)
                    description = segment.find('div', class_='segment__text__dsc').text.strip() if segment.find('div', class_='segment__text__dsc') else None
                    date_info = segment.find('div', class_='segment__date__deadline').text.strip() if segment.find('div', class_='segment__date__deadline') else None
                    date_text = date_info.replace('UTC +0', '').strip()
                    try:
                        date_obj = datetime.strptime(date_text, '%Y/%m/%d %H:%M:%S')
                        date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                        current_datetime = datetime.now()
                        if date_obj > current_datetime:
                            date = ''
                    except:
                        date =''
                    victim = re.sub(r'\s*PART[0-9]$', '', victim).replace(' SOLD','').replace('|','').strip()
                    appender(str(victim).replace('[\'','').replace('\']',''),'apt73',description,'',date,post_url)
        except Exception as e:
            errlog('atp73' + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
