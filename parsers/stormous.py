
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
            if filename.startswith('stormous-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('center')
                for div in divs_name:
                    title = div.find('p', {'class': 'h1'}).text
                    description = div.find("p", {"class": "description"}).text.strip()
                    appender(title, 'stormous', description)
                file.close()
        except:
            errlog('stormous: ' + 'parsing fail')
            pass