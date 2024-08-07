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
            if filename.startswith('karakurt-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('article', {"class": "ciz-post"})
                for div in divs_name:
                    title = div.h3.a.text.strip()
                    try:
                        description = div.find('div', {'class': 'post-des'}).p.text.strip()
                    except:
                        pass 
                        #errlog('karakurt: ' + 'parsing fail')
                    appender(title, 'karakurt', description.replace('\nexpand',''))
                divs_name=soup.find_all('div', {"class": "category-mid-post-two"})
                for div in divs_name:
                    title = div.h2.a.text.strip()
                    try:
                        description = div.find('div', {'class': 'post-des dropcap'}).p.text.strip()
                    except:
                        pass
                    #    errlog('karakurt: ' + 'parsing fail')
                    appender(title, 'karakurt', description.replace('\nexpand',' '))
                file.close()
        except:
            errlog('karakurt: ' + 'parsing fail')
            pass 