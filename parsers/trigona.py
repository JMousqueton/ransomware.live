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
            if filename.startswith('trigona-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "auction-item-info"})
                for div in divs_name:
                    title = div.find('a').text
                    description = div.find("div", {"class": "auction-item-info-text__content"}).text.strip()
                    appender(title, 'trigona', description)
                file.close()
        except:
            errlog('trigona: ' + 'parsing fail')
            pass

