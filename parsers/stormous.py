
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os,re
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('stormous-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                items = soup.find_all('div', class_='item')
                for item in items:
                    victim = item.find('h3').text.strip()
                    description = item.find('p').text.strip()
                    link = item.find('a')['href']
                    # button_link = item.find('a', href=True).get('href')
                    button_link = item.find('a', href=lambda href: href and 'DataPage' in href)['href']
                    url = find_slug_by_md5('stormous', extract_md5_from_filename(html_doc))
                    post_url = url.replace('stm.html','') + button_link
            
                    appender(victim,'stormous',description,'','',post_url)
                file.close()
        except:
            errlog('stormous: ' + 'parsing fail')
            pass 
