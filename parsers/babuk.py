
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |         X      |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

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
