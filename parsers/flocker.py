"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |      X         |                  |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime

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
