
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
