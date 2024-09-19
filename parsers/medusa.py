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
            if filename.startswith('medusa-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    link = div.get('data-id')
                    url = "cx5u7zxbvrfyoj6ughw76oa264ucuuizmmzypwum6ear7pct4yc723qd"
                    try:
                       post_url = 'http://' + url + '.onion/detail?id=' + link
                    except:
                        post_url = ''
                    try:
                        title = div.find('h3', {"class":"card-title"}).text
                        title = title.lstrip()
                        description = div.find("div", {"class": "card-body"}).text.strip()
                        published = div.find("div", {"class": "date-updated"}).text.strip() + '.000000'
                        #appender(title.rstrip(), 'medusa', description.replace('\n',' '),'',published,post_url)
                        appender(title.rstrip(), 'medusa', description,'',published,post_url)
                    except:
                        pass
                file.close()
        except Exception as e:
           stdlog('Medusa - parsing fail with error: ' + str(e))
        