"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('hellogookie-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    title = card.find('h5', class_='card-title').text.strip()
                    description = card.find('p', class_='card-text').text.strip()
                    link = card.find('a')['href']
                    post_url = find_slug_by_md5('hellogookie', extract_md5_from_filename(html_doc)) + link                    
                    appender(title, 'hellogookie',description,'','',post_url)
                file.close()
                 
        except:
            errlog('hellogookie : ' + 'parsing fail')
            pass
