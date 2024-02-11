"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |          X       |     X    |
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
            if filename.startswith('cryptnet-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "col-6 d-flex justify-content-end position-relative blog-div"})
                for div in divs_name:
                    title = div.find('h2').text.strip()
                    description = div.find("div",{"class":"head-info-body blog-head-info-body"}).find('a').text.strip()
                    appender(title, 'cryptnet', description)
                file.close()
        except:
            errlog('cryptnet: ' + 'parsing fail')
            pass

