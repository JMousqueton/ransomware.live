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
            if filename.startswith('babuk-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', class_='col-lg-4 col-sm-6 mb-4')
                for div in divs_name:
                    title = div.find('h5').text.strip()
                    publication_date = div.find('div', class_='published').text.strip() +  '.000000'
                    description = div.find('div', class_='col-12').text.strip()
                    link = 'http://nq4zyac4ukl4tykmidbzgdlvaboqeqsemkp4t35bzvjeve6zm2lqcjid.onion'+div.find('a')['href']
                    appender(title, 'babuk',description,'',publication_date,link)
                file.close()
        except:
            errlog("Babuk - Failed during : " + filename)

