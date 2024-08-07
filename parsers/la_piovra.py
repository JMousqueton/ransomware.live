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
            if filename.startswith('la_piovra-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs=soup.find_all('article')
                for article in divs:
                    # Extract the title
                    title = article.find('h2', class_='entry-title').text.strip()

                    # Extract the URL
                    url = article.find('h2', class_='entry-title').a['href']

                    # Extract the datetime
                    # Extract the datetime
                    datetime_str = article.find('time', class_='entry-date')['datetime']
                    datetime_obj = datetime.fromisoformat(datetime_str)
                    published = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

                    description = article.find('div',{"class" : "entry-content"}).text.strip()

                    appender(title, 'la_piovra', description,"",published,url)

                file.close()
        except:
            errlog('la_piovra : ' + 'parsing fail')
            pass
