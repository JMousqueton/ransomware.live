"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|              |               |        X         |    X     |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from parse import appender

def main():
    blacklist=['HOME', 'HOW TO DOWNLOAD?', 'ARCHIVE']
    for filename in os.listdir('source'):
        if filename.startswith('clop-'):
            html_doc='source/'+filename
            file=open(html_doc,'r')
            soup=BeautifulSoup(file,'html.parser')
            divs_name=soup.find_all('span', {"class": "g-menu-item-title"})
            for div in divs_name:
                for item in div.contents :
                    if item in blacklist:
                        continue
                    post_url= "http://santat7kpllt6iyvqbr7q4amdv6dzrh6paatvyrzl7ry3zm72zigf4ad.onion/" + str.lower(item.replace(".","-"))
                    appender(item, 'clop','_URL_','','',post_url)