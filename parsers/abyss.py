
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import stdlog, errlog
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('abyss-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('h5',{"class": "card-title"}).text.strip()
                    description = div.find('p',{"class" : "card-text"}).text.strip()
                    appender(title, 'abyss', description.replace('\n',''))
                file.close()
        except:
            errlog('blackbasta: ' + 'parsing fail')
            pass    