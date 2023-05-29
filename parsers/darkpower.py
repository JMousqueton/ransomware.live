"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |          X       |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from parse import appender
from sharedutils import errlog

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('darkpower-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "sm:w-1/2 mb-10 px-4"})
                for div in divs_name:
                    title = div.find('h2').text.strip()
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    website = div.find('a')
                    website = website.attrs['href']
                    post_url = 'http://' + url + '.onion/' + website
                    appender(title,'darkpower','','', '', post_url)
                file.close()                
        except:
            errlog('darkpower: ' + 'parsing fail')
            pass