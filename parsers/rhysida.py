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
            if filename.startswith('rhysida-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                div_containers = soup.find_all('div', class_='border m-2 p-2')
                for div in div_containers:
                    title_div = div.find('div', class_='m-2 h4')
                    title = title_div.text.strip() if title_div else ''
                    description_div = div.find('div', class_='m-2')
                    description = description_div.text.strip().replace('\n',' ') if description_div else ''
                    post_url=''
                    try:
                        post_url = 'archive.php?company=' + div.find('button')['data-company']
                    except:
                        pass
                    if len(title) != 0: 
                        appender(title, 'rhysida', description,"","",post_url)
                file.close()
        except:
            errlog('rhysida : ' + 'parsing fail')
            pass
