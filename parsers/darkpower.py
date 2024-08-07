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
            if filename.startswith('darkpower-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "sm:w-1/2 mb-10 px-4"})
                for div in divs_name:
                    title = div.find('h2').text.strip()
                    url = "powerj7kmpzkdhjg4szvcxxgktgk36ezpjxvtosylrpey7svpmrjyuyd"
                    website = div.find('a')
                    website = website.attrs['href']
                    post_url = 'http://' + url + '.onion/' + website
                    appender(title,'darkpower','','', '', post_url)
                file.close()                
        except:
            errlog('darkpower: ' + 'parsing fail')
            pass
