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
            if filename.startswith('werewolves-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                victim_elements = soup.find_all('div', class_='cart-block__content')

                for element in victim_elements: 
                    victim_name_element = element.find_previous('h2', class_='cart-block__title', itemprop='name')
                    victim_name = victim_name_element.text.strip()
                    
                    description = element.text.strip()
                    
                    published_time_element = element.find_next('time', itemprop='datePublished')
                    published_time = published_time_element['datetime'] if published_time_element else None
                    formatted_published_time = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S.%f")

                    post_link_element = element.find_next('div', class_='cart-block__timer')
                    if post_link_element:
                        post_link = find_slug_by_md5('werewolves', extract_md5_from_filename(html_doc)) + post_link_element['data-link'] 
                    else: 
                        post_link= ""
                    
    
                    appender(victim_name,'werewolves',description,'',formatted_published_time,post_link)
                file.close()
        except:
            errlog('werewolves: ' + 'parsing fail')
            pass    
