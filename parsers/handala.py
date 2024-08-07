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
            if filename.startswith('handala-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                posts = soup.find_all('li', class_='wp-block-post')
                for post in posts:
                    victim = post.find('h2', class_='wp-block-post-title').text.strip().replace(' Hacked','').replace('Zionists ','').replace('Zionist ','').replace(' Sensitive Leak','')
                    date_str = post.find('div', class_='wp-block-post-date').time['datetime']
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S.%f')
                    description = post.find('div', class_='wp-block-post-excerpt').text.strip()
                    link = post.find('h2', class_='wp-block-post-title').a['href']
                    appender(victim,'handala',description,'',date,link)
                file.close()
        except Exception as e:
            errlog('handala - parsing fail with error: ' + str(e))
