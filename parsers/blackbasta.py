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
            if filename.startswith('blackbasta-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('a', {"class": "blog_name_link"})
                    post = title.get('href').replace("https","http").replace(" ","%20")
                    title = title.text.strip()
                    descs = div.find_all('p')
                    description = ''
                    for desc in descs:
                        description += desc.text.strip()
                    appender(title, 'blackbasta', description.replace('\n',' ').replace('ADDRESS',' Address '),"","",post)
                file.close()
        except:
            errlog('blackbasta: ' + 'parsing fail')
            pass    
