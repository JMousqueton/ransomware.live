
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |          X       |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender
import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('play-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('th', {"class": "News"})
                for div in divs_name:
                    title = div.next_element.strip()
                    description = div.find('i', {'class': 'location'}).next_sibling.strip()
                    website = div.find('i', {'class': 'link'}).next_sibling.strip()
                    post_url = find_slug_by_md5('play', extract_md5_from_filename(html_doc)) + 'topic.php?id='+div['onclick'].split("'")[1] 
                    added_date = None
                    div_text = div.find_next('div', {'style': 'line-height: 1.70;'}).get_text()
                    if 'added:' in div_text:
                        added_date = div_text.split('added:')[1].split('publication date:')[0].strip()
                        now = datetime.datetime.now()
                        added_date = f"{added_date} {now.strftime('%H:%M:%S.%f')}"
                    appender(title, 'play', description, website,added_date,post_url)
                file.close()
        except:
            errlog('play: ' + 'parsing fail')
            pass    