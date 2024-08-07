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
            if filename.startswith('freecivilian-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('section', {"id": "openSource"})
                for div in divs_name:
                    for item in div.find_all('a',{'class':"a_href"}) :
                        # (item.text.replace(' - ','#').split('#')[0].replace('+','').strip())
                        appender(item.text.replace(' - ','#').split('#')[0].replace('+','').strip(),'freecivilian')
            file.close()                
        except:
            # errlog('freecivilian: ' + 'parsing fail')
            pass
