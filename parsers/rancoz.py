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
            if filename.startswith('rancoz-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('tr', {"class": "trow"})
                for div in divs_name:
                    title = div.find_all('td')[0].text.strip()
                    description = div.find_all('td')[2].text.strip()
                    url = 'ze677xuzard4lx4iul2yzf5ks4gqqzoulgj5u4n5n4bbbsxjbfr7eayd'
                    link = div.find('a')
                    link = link.get('href')
                    post_url = 'http://' + url + '.onion' + link
                    appender(title, 'rancoz', description,'','',post_url)
                file.close()
        except:
            errlog('rancoz: ' + 'parsing fail')
            pass    
