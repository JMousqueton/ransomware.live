"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('clop-a'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                tbody = soup.find('tbody')
                trs  = tbody.find_all('tr') # type: ignore
                for tr in trs:
                    tds = tr.find_all('td')
                    victim = tds[0].text.strip()
                    #description = tds[2].text.strip()
                    appender(victim, 'clop','_URL_')
                    #print(victim)
        except:
            errlog('clop-torrent: ' + 'parsing fail')
            pass