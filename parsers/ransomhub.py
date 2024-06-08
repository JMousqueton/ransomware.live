
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
import re
from datetime import datetime

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
                    title = title_tag.get_text(strip=True).replace('(SOLD)','').replace('<SOLD>','')
                    url = find_slug_by_md5('ransomhub', extract_md5_from_filename(html_doc))
                    link = card.find_parent('a')['href']
                    post_date = convert_date(card.find('div', class_='card-footer').get_text(strip=True))
                    post_url= url + '/' + link
                    appender(title, 'ransomhub',"","",post_date,post_url)
                file.close()
        except Exception as e:
            errlog('ransomhub - parsing fail with error: ' + str(e))