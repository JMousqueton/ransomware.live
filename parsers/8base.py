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
            if filename.startswith('8base-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', class_='list-group-item')
                for div in divs_name:
                    link = div.find('a')['href']
                    name = div.find('a').text.strip()
                    tmp = div.find('div', class_='d-flex gap-2 small mt-1 opacity-25').text.strip()
                    date_string = tmp.splitlines()[0].replace("Downloaded: ","")
                    try: 
                        published = datetime.strptime(date_string, "%d.%m.%Y").strftime("%Y-%m-%d %H:%M:%S.%f")
                    except: 
                        published = datetime.strptime(date_string, "%d.%m.%y").strftime("%Y-%m-%d %H:%M:%S.%f")
                    description = div.find('div', class_='small opacity-50').text.strip()
                    appender(name, '8base', description.replace('\n',' '),"",published,link)
                file.close()
        except:
           errlog('8base : ' + 'parsing fail')
           pass    
