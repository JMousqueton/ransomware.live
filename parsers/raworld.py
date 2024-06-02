"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
from datetime import datetime


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('raworld-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                # Find all div elements with class "portfolio-content"
                divs = soup.find_all("div", class_="portfolio-content")
                # Iterate over each div and extract the link and href
                for div in divs:
                    link = div.find("a")  # Find the <a> tag
                    if link:
                        href = link.get("href")  # Get the href attribute of the <a> tag
                        url = href.replace('./',find_slug_by_md5('raworld', extract_md5_from_filename(html_doc))+'/')
                        victim = link.text  # Get the text inside the <a> tag
                        appender(victim,'raworld',"","","",url)
                file.close()
        except:
            errlog('raworld: ' + 'parsing fail')
            pass
