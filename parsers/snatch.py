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
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('snatch-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "ann-block"})
                for div in divs_name:
                    title = div.find('div', {'class': 'a-b-n-name'}).text.strip()
                    published = div.find('div', {'class': 'a-b-h-time'}).text.strip()
                    date_obj = datetime.strptime(published, '%b %d, %Y %I:%M %p')
                    published = datetime.strftime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
                    link = div.find('button', {'class': 'a-b-b-r-l-button'})
                    link = link['onclick'].replace('window.location=','')
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    link = 'http://' + url + '.onion/' + link 
                    description = div.find('div', {'class': 'a-b-text'}).text.strip()
                    appender(title, 'snatch', description,"",published,link.replace('\'',''))
                file.close()
        except:
            errlog('snatch: ' + 'parsing fail')
            pass