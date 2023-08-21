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
                div = soup.find('div',{"class":"di"})
                divs_name=div.find_all('a')
                for a in divs_name:
                    victim = a.text.strip().replace('{','').replace('}','')
                    url = a['href']
                    post_url = find_slug_by_md5('ransomed', extract_md5_from_filename(html_doc)) + url
                    appender(victim, 'ransomed','','','',post_url)
                file.close()
        except:
            errlog('ransomed: ' + 'parsing fail')
            pass    
