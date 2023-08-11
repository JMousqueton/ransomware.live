"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|              |               |        X         |          |
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
            if filename.startswith('clop-a'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs = soup.find("div", class_="datagrid")
                trs = divs.find_all("tr")
                for tr in trs:
                    td = tr.find("td")
                    if td: # if there is a <td> tag, get the name and link
                        name = td.get_text().strip() # get the text inside the <td> tag as the name
                        appender(name, 'clop','_URL_')
        except:
            errlog('clop-torrent: ' + 'parsing fail')
            pass
