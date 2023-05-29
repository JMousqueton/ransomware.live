"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('mallox-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card mb-4 box-shadow"})
                for div in divs_name:
                    title = div.find('h5',{"class": "card-title"}).text.strip()
                    description = ''
                    for p in div.find_all('p'):
                        description+=p.text + ' '
                    post = div.find('a', {'class': 'btn btn-primary btn-sm'})
                    post = post.get('href')
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    url = 'http://' + url + '.onion' + post
                    publish = div.find('span', {'class': 'badge badge-info'}).text.strip()
                    date_obj = datetime.strptime(publish, "%d/%m/%Y %H:%M")
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title, 'mallox', description,"",formatted_date,url)
                file.close()
        except:
            errlog('mallox: ' + 'parsing fail')
            pass