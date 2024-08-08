
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
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender, clean_slug


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('alphalocker-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', class_='b_block')
                for div in divs_name:
                    header = div.find('a', class_="a_title")
                    title = header.text.strip()
                    title=clean_slug(title)
                    url = header.get('href') or header['href'] 
                    description = div.find('div', style='line-height:20px; padding-top:5px; margin-bottom:30px;').text.strip()
                    try:
                        url = find_slug_by_md5('alphalocker', extract_md5_from_filename(html_doc)).replace('_1','') + "/" + str(url)
                    except:
                        url = 'http://mydatae2d63il5oaxxangwnid5loq2qmtsol2ozr6vtb7yfm5ypzo6id.onion' +  "/" + str(url)
                    appender(title, 'alphalocker', description,"","",url)
                file.close()
        except:
            errlog("Failed during : " + filename)
