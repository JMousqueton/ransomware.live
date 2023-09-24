
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""



import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename, remove_multiple_spaces
from parse import appender
from datetime import datetime


def main():
    for filename in os.listdir('source'):
        #try:
            if filename.startswith('threeam-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                post_divs = soup.find_all('div', class_='post')
                for post_div in post_divs:
                    post_title = post_div.find('div', class_='post-title-block').text.strip()
                    victim  = post_title.split('\n')[0].strip()
                    description = post_div.find('div', class_='post-text').text.strip()
                    link = post_div.find('a', class_='post-more-link')
                    if link:
                        onclick_attr = link.get('onclick')
                        url = find_slug_by_md5('threeam', extract_md5_from_filename(html_doc))
                        post = url +  onclick_attr.split("'")[1]
                    appender(victim, 'threeam', remove_multiple_spaces(description),victim,'',post)
                file.close()
        #except:
        #    errlog("Failed during : " + filename)
