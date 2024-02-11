
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import stdlog, errlog
from parse import appender
from datetime import datetime

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
