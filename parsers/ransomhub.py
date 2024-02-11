
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
                for post in posts:
                    title_element = post.find('h5', class_='card-title').find('a')
                    match = re.match(r"^(.*?)<([^>]*)>", title_element.text)
                    title = match.group(1).strip()  # Group 1: String before '<'
                    website = match.group(2).strip()  # Group 2: String between '<' and '>'
                    post_url = find_slug_by_md5('ransomhub', extract_md5_from_filename(html_doc)) + title_element['href']

                    # date_element = post.find('div', class_='countdown-date')
                    # description = date_element.text

                    appender(title, 'ransomhub', '',website,'',post_url)

                file.close()
        except:
            errlog('ransomhub : ' + 'parsing fail')
            pass
