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
                        errlog('lockbit3a - parsing fail with error: ' + str(e))
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
                        errlog('lockbit3b - parsing fail with error: ' + str(e))
                divs_name=soup.find_all('a', {"class": "post-block bad"})
                for div in divs_name:
                    try:
                        title = div.find('div',{"class": "post-title"}).text.strip()
                        description = div.find('div',{"class" : "post-block-text"}).text.strip()
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        link = div['href']
                        #url = find_slug_by_md5('lockbit3', extract_md5_from_filename(html_doc))
                        url = 'http://lbb6ud2vyf23z4hw6fzskr5gru7eftbjfbd6yzra3hzuqqvjy63blqqd.onion/'
                        post = url  + link
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        date_obj = datetime.strptime(published.replace('Updated: ',''), "%d %b, %Y,\xa0\xa0 %H:%M %Z")
                        published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                        parse.appender(title, 'lockbit3', description.replace('\n',' '),"",published,post)
                    except Exception as e:
                        errlog('lockbit3c - parsing fail with error: ' + str(e))
                divs_name=soup.find_all('a', {"class": "post-block good"})
                for div in divs_name:
                    try:
                        title = div.find('div',{"class": "post-title"}).text.strip()
                        description = div.find('div',{"class" : "post-block-text"}).text.strip()
                        link = div['href']
                        #url = find_slug_by_md5('lockbit3', extract_md5_from_filename(html_doc))
                        url = 'http://lockbit3753ekiocyo5epmpy6klmejchjtzddoekjlnt6mu3qh4de2id.onion/'
                        post = url  + link
                        published = div.find('div',{"class" : "updated-post-date"}).text.strip()
                        date_obj = datetime.strptime(published.replace('Updated: ',''), "%d %b, %Y,\xa0\xa0 %H:%M %Z")
                        published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                        parse.appender(title, 'lockbit3', description.replace('\n',' '),"",published,post)
                    except Exception as e:
                        errlog('lockbit3d - parsing fail with error: ' + str(e) + ' for victim: '+ title)
                file.close()
        except Exception as e:
            errlog('lockbit3e - parsing fail with error: ' + str(e) + 'in file:' + filename)
