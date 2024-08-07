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
            if filename.startswith('losttrust-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                
                # Find all div elements with class "card" (assuming there may be more companies)
                companies = soup.find_all('div', class_='card')

                # Iterate through each company
                for company in companies:
                    try: 
                        victim = company.find('div', class_='card-header').text.strip()
                    except: 
                        continue
                    description = company.find('div', class_='card-body').p.text.strip()
                    website = company.find('a', href=True, text='Visit site')['href']
                    appender(victim, 'losttrust', description.replace('\n',' '),"https://"+website)
                file.close()
        except:
            errlog('losttrust: ' + 'parsing fail')
            pass    
