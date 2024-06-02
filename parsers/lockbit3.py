"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
Codé par @JMousqueton pour Ransomware.live
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog,stdlog
from sharedutils import find_slug_by_md5, extract_md5_from_filename
import parse
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('lockbit3-'):
                html_doc='source/'+filename
                #stdlog('Processing ' + filename)
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "post-block bad"})
                for div in divs_name:
                    try:
                        post = div['onclick'].split("'")[1]
                        url = find_slug_by_md5('lockbit3', extract_md5_from_filename(html_doc))
                        post = url  + post
                        title = div.find('div',{"class": "post-title"}).text.strip()
                        description = div.find('div',{"class" : "post-block-text"}).text.strip()
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        date_obj = datetime.strptime(published.replace('Updated: ',''), "%d %b, %Y,\xa0\xa0 %H:%M %Z")
                        published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                        parse.appender(title, 'lockbit3', description.replace('\n',' '),"",published,post)
                    except Exception as e:
                        errlog('lockbit3 - parsing fail with error: ' + str(e))
                divs_name=soup.find_all('div', {"class": "post-block good"})
                for div in divs_name:
                    try: 
                        post = div['onclick'].split("'")[1]
                        url = find_slug_by_md5('lockbit3', extract_md5_from_filename(html_doc))
                        post = url  + post
                        title = div.find('div',{"class": "post-title"}).text.strip()
                        description = div.find('div',{"class" : "post-block-text"}).text.strip()
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        date_obj = datetime.strptime(published.replace('Updated: ',''), "%d %b, %Y,\xa0\xa0 %H:%M %Z")
                        published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                        parse.appender(title, 'lockbit3', description.replace('\n',' '),"",published,post)
                    except Exception as e:
                        errlog('lockbit3 - parsing fail with error: ' + str(e))
                divs_name=soup.find_all('a', {"class": "post-block bad"})
                for div in divs_name:
                    try:
                        title = div.find('div',{"class": "post-title"}).text.strip()
                        description = div.find('div',{"class" : "post-block-text"}).text.strip()
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        link = div['href']
                        url = find_slug_by_md5('lockbit3', extract_md5_from_filename(html_doc))
                        post = url  + link
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        date_obj = datetime.strptime(published.replace('Updated: ',''), "%d %b, %Y,\xa0\xa0 %H:%M %Z")
                        published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                        parse.appender(title, 'lockbit3', description.replace('\n',' '),"",published,post)
                    except Exception as e:
                        errlog('lockbit3 - parsing fail with error: ' + str(e))
                divs_name=soup.find_all('a', {"class": "post-block good"})
                for div in divs_name:
                    try:
                        title = div.find('div',{"class": "post-title"}).text.strip()
                        description = div.find('div',{"class" : "post-block-text"}).text.strip()
                        link = div['href']
                        url = find_slug_by_md5('lockbit3', extract_md5_from_filename(html_doc))
                        post = url  + link
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        date_obj = datetime.strptime(published.replace('Updated: ',''), "%d %b, %Y,\xa0\xa0 %H:%M %Z")
                        published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                        parse.appender(title, 'lockbit3', description.replace('\n',' '),"",published,post)
                    except Exception as e:
                        errlog('lockbit3 - parsing fail with error: ' + str(e) + ' for victim: '+ title)
                file.close()
        except Exception as e:
            errlog('lockbit3 - parsing fail with error: ' + str(e) + 'in file:' + filename)
