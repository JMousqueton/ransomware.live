
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |    X     |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomed-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name  = soup.find_all('li',{"class":"wp-block-post"})
                for div in divs_name:
                    meta = div.find('a')
                    title = meta.text.strip()
                    description = div.find('div',{"class":"wp-block-post-excerpt"}).text.strip()
                    link = meta["href"]
                    appender(title, 'ransomed',description,'','',link)
                file.close()
        except:
            errlog('ransomed: ' + 'parsing fail')
            pass    
