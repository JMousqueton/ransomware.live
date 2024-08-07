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
            if filename.startswith('flocker-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                entries = soup.find_all('h2', class_='entry-title ast-blog-single-element')
                for entry in entries:
                    victim_name = entry.text.strip()
                    link = entry.find('a')['href']
                    parent_div = entry.find_parent('article')
                    date_span = parent_div.find('span', itemprop='datePublished')
                    if date_span:
                        date = date_span.text.strip()
                        parsed_date = datetime.strptime(date, '%B %d, %Y')
                        date = parsed_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                        date = ''
                    description = entry.find_next_sibling('div', class_='ast-excerpt-container ast-blog-single-element').text.strip()
                    appender(victim_name,'flocker',description,'',date,link)
        except:
            errlog('flocker : ' + 'parsing fail')
            pass