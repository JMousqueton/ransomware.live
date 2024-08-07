"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('blackout-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all("div", class_="card")
                for card in cards:
                    # Extract link name
                    title = card.find("a", class_="text-white").text.strip()
                    # Extract link
                    link = card.find("a", class_="text-white")["href"]
                    # Extract card text
                    description = card.find("p", class_="card-text").text.strip()
                    url = find_slug_by_md5('blackout', extract_md5_from_filename(html_doc)) + str(link)
                    appender(title, 'blackout', description,"","",url)
                file.close()
        except:
            errlog("Failed during : " + filename)
