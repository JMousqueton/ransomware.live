
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |      X         |                 |     x    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os, re
from datetime import datetime
from bs4 import BeautifulSoup
from sharedutils import stdlog, errlog
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('8base-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', class_='list-group-item')
                for div in divs_name:
                    link = div.find('a')['href']
                    name = div.find('a').text.strip()
                    tmp = div.find('div', class_='d-flex gap-2 small mt-1 opacity-25').text.strip()
                    date_string = tmp.splitlines()[0].replace("Downloaded: ","")
                    published = datetime.strptime(date_string, "%d.%m.%Y").strftime("%Y-%m-%d %H:%M:%S.%f")
                    description = div.find('div', class_='small opacity-50').text.strip()
                    appender(name, '8base', description.replace('\n',' '),"",published,link)
                file.close()
        except:
           errlog('8base : ' + 'parsing fail')
           pass    
