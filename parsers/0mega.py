"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('0mega-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                rows = soup.select('.datatable tr.trow') #[1:]
                for row in rows:
                    columns = row.find_all('td')
                    title = columns[0].get_text(strip=True)
                    last_updated_date_str = columns[4].get_text(strip=True)
                    pubdate = datetime.strptime(last_updated_date_str, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S.%f")
                    description = columns[2].get_text(strip=True)
                    link = columns[5].find('a')['href']
                    link = url = find_slug_by_md5('0mega', extract_md5_from_filename(html_doc)) +str(link)
                    appender(title, '0mega', description,"",pubdate,link)
                file.close()
        except Exception as e:
            errlog('0mega - parsing fail with error: ' + str(e) + 'in file:' + filename) 