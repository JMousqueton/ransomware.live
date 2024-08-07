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
            if filename.startswith('vicesociety-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('td',{"valign":"top"})
                for div in divs_name:
                    try:
                        title = div.find("font", {"size":4}).text.strip() 
                        for description in div.find_all("font", {"size":2, "color":"#5B61F6"}):
                            if description.b.text.strip().startswith("http"):
                                website = description.get_text()
                            if not description.b.text.strip().startswith("http"):
                                desc = description.get_text()
                                appender(title, 'vicesociety', desc,website)
                    except:
                        pass
                file.close()
        except:
            errlog('vicesociety: ' + 'parsing fail')
            pass