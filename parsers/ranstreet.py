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
        #try:
            if filename.startswith('ranstreet-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                all_tr_elements = soup.find_all('tr')
                for tr in all_tr_elements:
                    th_element = tr.find('th')  # Find the first <th> within each <tr>
                    if th_element:
                        company_name = th_element.text.strip().replace('C0MPANY [', '').replace(']', '')
                        appender(company_name,'ranstreet')
                file.close()
        #except:
        #    errlog('ranstreet: ' + 'parsing fail')
        #    pass    
