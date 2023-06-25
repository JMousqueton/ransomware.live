
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
from sharedutils import errlog
from parse import appender
import re
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('blacksuit-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs=soup.find_all('div', {"class": "card"})
                for article in divs:
                    # Extract the title
                    title = article.find('div', class_='title').text.strip()

                    # Extract the URL
                    parts = filename.split('-')
                    url_site = parts[1].replace('.html','')
                    url = article.find('div', class_='title').a['href']
                    post_url = 'http://' + url_site + '.onion/' +  url

                    website= article.find('div', class_='url').a['href']
                    try:
                        description = article.find('p').text.strip().replace('\n', ' ')
                    except:
                        description = ''
                    appender(title, 'blacksuit', description,website,'',post_url)

                file.close()
        except:
            errlog('blacksuit : ' + 'parsing fail')
            pass
