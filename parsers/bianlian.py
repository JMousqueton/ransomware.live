
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('bianlian-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('section', {"class": "list-item"})
                for div in divs_name:
                    title = div.h1.text.strip()
                    post = div.find('a', {'class': 'readmore'})
                    post = post.get('href')
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    description = div.div.text.strip()
                    appender(title, 'bianlian', description,"","",'http://' + url + '.onion' + post)
                file.close()
        except:
            errlog("Failed during : " + filename)