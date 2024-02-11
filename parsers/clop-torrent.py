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
from sharedutils import errlog

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('clop-a'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                tbody = soup.find('tbody')
                trs  = tbody.find_all('tr') # type: ignore
                for tr in trs:
                    tds = tr.find_all('td')
                    victim = tds[0].text.strip()
                    #description = tds[2].text.strip()
                    #appender(victim, 'clop','_URL_')
                    print(victim)
        except:
            errlog('clop-torrent: ' + 'parsing fail')
            pass