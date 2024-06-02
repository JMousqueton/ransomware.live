
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
            if filename.startswith('blacksuit-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs=soup.find_all('div', {"class": "card"})
                for article in divs:
                    # Extract the title
                    title = article.find('div', class_='title').text.strip()
                    title = title.replace('amp;','')
                    # Extract the URL
                    url_site = find_slug_by_md5('blacksuit', extract_md5_from_filename(html_doc))
                    #url_site = "weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd"
                    url = article.find('div', class_='title').a['href']
                    post_url = url_site + '/' +  url

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
