
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

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('hellogookie-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    title = card.find('h5', class_='card-title').text.strip()
                    description = card.find('p', class_='card-text').text.strip()
                    link = card.find('a')['href']
                    post_url = find_slug_by_md5('hellogookie', extract_md5_from_filename(html_doc)) + link
                    #print(f"Title: {title}")
                    #print(f"Description: {description}")
                    #print(f"Link: {post_url}\n")
                    
                    appender(title, 'hellogookie',description,'','',post_url)
                file.close()
                 
        except:
            errlog('hellogookie : ' + 'parsing fail')
            pass
