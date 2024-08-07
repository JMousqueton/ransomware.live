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
            if filename.startswith('abyss-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('h5',{"class": "card-title"}).text.strip()
                    description = div.find('p',{"class" : "card-text"}).text.strip()
                    appender(title, 'abyss', description.replace('\n',' '))
                file.close()
        except:
            errlog('blackbasta: ' + 'parsing fail')
            pass    