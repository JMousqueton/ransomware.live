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

def convert_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return date_str

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomhub-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    title_tag = card.find('div', class_='card-title').strong
                    title = title_tag.get_text(strip=True).replace('(SOLD)','').replace('<SOLD>','').replace('<','').replace('>','').replace('<Disclose>','').replace('Updated','')
                    url = find_slug_by_md5('ransomhub', extract_md5_from_filename(html_doc))
                    #url = "http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion"
                    link = card.find_parent('a')['href']
                    post_date = convert_date(card.find('div', class_='card-footer').get_text(strip=True))
                    post_url= url + '/' + link
                    appender(title, 'ransomhub',"","",post_date,post_url)
                file.close()
        except Exception as e:
            errlog('ransomhub - parsing fail with error: ' + str(e))
