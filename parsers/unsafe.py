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
            if filename.startswith('unsafe-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "info"})
                for div in divs_name:
                    title = str(div.find('h4').get_text())
                    titre_h6 = div.find_all("h6")
                    website = ''
                    country = ''
                    revenue = ''
                    for info in titre_h6:
                        if "website" in str(info.text):
                            website = re.sub(r'[^a-zA-Z0-9\.:/]', '', str(info.text.replace('website: ','https://')))
                        if "country" in str(info.text): 
                            country = str(info.text)
                        if "revenue" in str(info.text): 
                            revenue = str(info.text)
                    description = country + ' -' + revenue
                    appender(title, 'unsafe', description, website)
        except:
            errlog('unsafe: ' + 'parsing fail')
            pass