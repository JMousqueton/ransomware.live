
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |          X       |          |
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
            if filename.startswith('play-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('th', {"class": "News"})
                for div in divs_name:
                    title = div.next_element.strip()
                    description = div.find('i', {'class': 'location'}).next_sibling.strip()
                    website = div.find('i', {'class': 'link'}).next_sibling.strip()
                    appender(title, 'play', description, website)
                file.close()
        except:
            errlog('play: ' + 'parsing fail')
            pass    