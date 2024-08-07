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
