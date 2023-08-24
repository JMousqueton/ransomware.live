"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('cloak-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                main_items = soup.find_all('div', class_='main__items')
                for item in main_items:
                    victim = item.find('h2').get_text()
                    description = item.find('p', class_='main__country').get_text()
                    link_element = item.find('a', class_='main__link')
                    url = ''
                    try:
                        link = link_element['href'] 
                        if link_element:
                            url = find_slug_by_md5('cloak', extract_md5_from_filename(html_doc))
                            url =  url + link
                    except: 
                       pass

                    appender(victim, 'cloak',description,'','',url)
                file.close()
        except:
            errlog('cloak: ' + 'parsing fail')
            pass
