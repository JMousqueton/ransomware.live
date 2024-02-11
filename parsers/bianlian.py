
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
            if filename.startswith('bianlian-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('section', {"class": "list-item"})
                for div in divs_name:
                    title = div.h1.text.strip()
                    post = div.find('a', {'class': 'readmore'})
                    post = post.get('href')
                    try:
                        url = find_slug_by_md5('bianlian', extract_md5_from_filename(html_doc)) + str(post)
                    except:
                        #url = ''
                        url = "bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion" + str(post)
                    description = div.div.text.strip()
                    description = description.replace('%20',' ')
                    appender(title, 'bianlian', description,"","",url)
                file.close()
        except:
            errlog("Failed during : " + filename)
