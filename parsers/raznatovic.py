"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
import json
import html
from sharedutils import errlog
from parse import appender 
import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('raznatovic-'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name = soup.find_all('div',{"class":"card"})
                for div in divs_name:
                    if 'id' in div:
                        continue
                    try: 
                        title = div.b.u.text.strip()
                    except:
                        continue
                    description = div.find('ul').text.strip()
                    description = ' '.join(description.split())
                    link = div.find('a')['href']
                    if not link.startswith('https://'):
                        link = 'https://ransomed.vc' + link
                    print('-------')
                    appender(title,'raznatovic',description.replace('\n',' - '),'','',link)
                file.close()
        except:
            errlog('raznatovic: ' + 'parsing fail')
            pass    
