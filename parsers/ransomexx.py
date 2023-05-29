"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |          X       |     X    |
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
            if filename.startswith('ransomexx-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card-body"})
                for div in divs_name:
                    title = div.find('h5').text.strip()
                    description = div.find_all('p', {"class", "card-text"})[1].text.strip()
                    link = div.find('a', {"class", "btn btn-outline-primary"})
                    link = link.get('href')
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    post_url = 'http://' + url + '.onion' + link
                    appender(title, 'ransomexx', description,"","",post_url)
                file.close()
        except:
            errlog('ransomexx: ' + 'parsing fail')
            pass
