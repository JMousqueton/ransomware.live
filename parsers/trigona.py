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
            if filename.startswith('trigona-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                #divs_name=soup.find_all('a', class_=["_m _preview grid__item", "_l _leaked grid__item"])
                div = soup.find('div', {"class": "grid"})
                divs_name = div.find_all('a') 
                for div in divs_name:
                    #title = div.find('div', class_='grid-caption__title')
                    title = div.find('div', {"class": "grid-caption__title"}).contents[0].strip() 
                    #victim = title.text.strip().replace('\n','')
                    #victim = re.split(r'  ',victim)[0]
                    post = div.get('href')
                    address  = find_slug_by_md5('trigona', extract_md5_from_filename(html_doc)) 
                    url = address + post
                    appender(title, 'trigona', '','','',url)
                file.close()
        except:
            errlog('trigona: ' + 'parsing fail')
            pass

