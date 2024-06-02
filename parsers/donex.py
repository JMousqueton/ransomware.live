
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |         X      |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
from datetime import datetime 


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('donex-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                posts = soup.find_all('div', class_='post')
                for post in posts:
                    title = post.find('a', class_='post-title').text
                    link = post.find('a', class_='post-title')['href']
                    pub_date = post.find('div', class_='post-date').text
                    # Convert date format
                    date_obj = datetime.strptime(pub_date, '%Y.%m.%d')
                    pub_date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    description = post.find('div', class_='post-except').text.strip().replace('\n',' ')
                    description = ' '.join(description.split())
                    try: 
                        url = find_slug_by_md5('donex', extract_md5_from_filename(html_doc)) + str(link)
                    except:
                        url =''

                    appender(title, 'donex', description,"",pub_date,url)
                file.close()
        except:
            errlog("Failed during : " + filename)
