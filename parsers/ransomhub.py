
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
import re
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomhub-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                posts = soup.find_all('div', class_='timeline-item')
                for div in posts:
                    tmp = div.find('a')
                    s = tmp.text.strip()
                    parts = s.split('<')
                    title = parts[0]
                    if '<' in s:
                        website = parts[1].split('>')[0]
                    else:
                        website = ''
                    description = div.find('p',{"class" : "card-text"}).text.strip().replace('Data',' Data').replace('Published',' Published')
                    post_url = find_slug_by_md5('ransomhub', extract_md5_from_filename(html_doc)) + tmp['href']
                    appender(title, 'ransomhub',description,website,'',post_url)
                file.close()
        except Exception as e:
            errlog('ransomhub - parsing fail with error: ' + str(e))
