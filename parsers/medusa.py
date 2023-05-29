
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

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('medusa-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    link = div.get('data-id')
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    post_url = 'http://' + url + '.onion/detail?id=' + link
                    title = div.find('h3', {"class":"card-title"}).text
                    description = div.find("div", {"class": "card-body"}).text.strip()
                    published = div.find("div", {"class": "date-updated"}).text.strip() + '.12345'
                    appender(title, 'medusa', description,'',published,post_url)
                file.close()
        except:
            errlog('medusa: ' + 'parsing fail')
            pass