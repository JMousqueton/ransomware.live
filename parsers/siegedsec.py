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
from sharedutils import errlog, stdlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('siegedsec-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                
                rows = soup.find_all('tr')[1:]  # Exclude the first row (header)

                for row in rows:
                    columns = row.find_all('td')
                    victim = columns[0].get_text()
                    description = columns[2].get_text()
                    last_updated = columns[4].get_text()
                    last_updated_datetime = datetime.strptime(last_updated, "%Y-%m-%d")
                    published = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
                    link = find_slug_by_md5('siegedsec', extract_md5_from_filename(html_doc)) + "/" + columns[5].find('a')['href']
                    appender(victim, 'siegedsec', description.replace('\n',' '),"",published,link)
                file.close()
        except:
           errlog('siegedsec : ' + 'parsing fail')
           pass    
