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
            if filename.startswith('darkrace-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all("li", {"class": "post-list-item"})
                for div in divs_name:
                    title = div.find("h2").text
                    date_string = div.find("p", {"class": "post-info"}).text.strip()
                    date_object = datetime.strptime(date_string, "%m/%d/%Y")
                    published = date_object.strftime("%Y-%m-%d 00:00:00.00000")
                    description = div.find("div").text
                    link = div.find("a", {"class": "read-more"})["href"]
                    parts = filename.split('-')
                    site = parts[1].replace('.html','')
                    post_url = 'http://' + site + '.onion' + link
                    appender(title, 'darkrace', description, '', published, post_url)
                file.close()
        except:
            errlog('ragroup: ' + 'parsing fail')
            pass    


main()
