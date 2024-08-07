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
            if filename.startswith('metaencryptor-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card-header')
                for card in cards:
                   for card in cards:
                    victim = card.get_text(strip=True)
                    description = card.find_next('p', class_='card-text').get_text(strip=True)
                    
                    website_link = card.find_next('a', class_='btn btn-secondary btn-sm')
                    website = website_link['href'] if website_link else None
                    
                    post_link = card.find_next('a', class_='btn btn-primary btn-sm')
                    if post_link:
                        # post_url = "https://metacrptmytukkj7ajwjovdpjqzd7esg5v3sg344uzhigagpezcqlpyd.onion" + post_link['href']
                        post_url = find_slug_by_md5('metaencryptor', extract_md5_from_filename(html_doc)) +  post_link['href']
                    else:
                        post_url =  None
                    appender(victim, 'metaencryptor', description, website, '', post_url)
                file.close()
        except Exception as e:
            errlog('metaencryptor - parsing fail with error: ' + str(e))
