"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('trisec-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                victim_links = soup.find_all('a', href=lambda href: href and not href.endswith("index.html"))
                for link in victim_links:
                    if link['href'] != "#" and not link['href'].endswith("index.html"):
                        url = find_slug_by_md5('trisec', extract_md5_from_filename(html_doc)).replace('victim.html','') + link['href']
                        victim = link.text.replace('[*] ','')
                        appender(victim, 'trisec', "","","",url)
                file.close()
        except:
            errlog("Failed during : " + filename)
