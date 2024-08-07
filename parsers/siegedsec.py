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
