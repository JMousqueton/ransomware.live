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
            if filename.startswith('everest-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('article')
                for div in divs_name:
                    tmp = div.find('h2', {"class": "entry-title heading-size-1"})
                    title = tmp.a.string
                    title = title.replace(' Data Leak','')
                    a_tag = tmp.find('a')
                    url = a_tag['href']
                    description = div.find('div', {"class": "entry-content"}).p.text.strip()
                    appender(title, 'everest',description,'','',url)
                file.close()
        except:
            errlog("Everest - Failed during : " + filename)

