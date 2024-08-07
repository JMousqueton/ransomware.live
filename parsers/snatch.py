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
            if filename.startswith('snatch-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "ann-block"})
                for div in divs_name:
                    title = div.find('div', {'class': 'a-b-n-name'}).text.strip()
                    published = div.find('div', {'class': 'a-b-h-time'}).text.strip()
                    date_obj = datetime.strptime(published, '%b %d, %Y %I:%M %p')
                    published = datetime.strftime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
                    link = div.find('button', {'class': 'a-b-b-r-l-button'})
                    link = link['onclick'].replace('window.location=','')
                    url = 'hl66646wtlp2naoqnhattngigjp5palgqmbwixepcjyq5i534acgqyad'
                    link = 'http://' + url + '.onion/' + link 
                    description = div.find('div', {'class': 'a-b-text'}).text.strip()
                    appender(title, 'snatch', description,"",published,link.replace('\'',''))
                file.close()
        except:
            errlog('snatch: ' + 'parsing fail')
            pass