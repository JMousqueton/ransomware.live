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
            if filename.startswith('daixin-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('section', class_='card')
                for card in cards:
                    title = card.find('h4', class_='card-title').text.strip()
                    website = card.find('a').get('href')
                    description_tag = card.find('p', class_='card-text')
                    description = description_tag.text.strip() if description_tag else ""
                    appender(title, 'daixin', description, website)
                file.close()
        except:
            stdlog("Failed during : " + filename)
