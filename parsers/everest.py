
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |         X      |                  |     X    |
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
            if filename.startswith('everest-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('article')
                for div in divs_name:
                    tmp = div.find('h2', {"class": "entry-title heading-size-1"})
                    title = tmp.a.string
                    title = title.replace(' Data Leak','')
                    a_tag = tmp.find('a')
                    url = a_tag['href']
                    description = div.find('div', {"class": "entry-content"}).p.text.strip()
                    appender(title, 'everest',description,'','',url)
                file.close()
        except:
            errlog("Everest - Failed during : " + filename)

