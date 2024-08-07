"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


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
