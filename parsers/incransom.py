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
from urllib.parse import urlparse

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


def main():
    for filename in os.listdir('source'):
        #try:
             if filename.startswith(__name__.split('.')[-1]+'-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('a', {"class":"flex flex-col justify-between w-full h-56 border-t-4 border-2 border-t-green-500 dark:border-gray-900 dark:border-t-green-500 rounded-[20px] bg-white dark:bg-navy-800"})
                for div in divs_name:
                    section = div.find('span',{"class": "dark:text-gray-600"})
                    title = section.text.strip()
                    description = div.find('span',{"class": "text-sm dark:text-gray-600"}).text.strip()
                    link = div['href']
                    appender(title,'incransom',description,'',date,link)

                divs_name=soup.find_all('a', {"class":"flex flex-col justify-between w-full h-56 border-t-4 border-2 border-t-red-500 dark:border-gray-900 dark:border-t-red-500 rounded-[20px] bg-white dark:bg-navy-800"})
                for div in divs_name:
                    section = div.find('span',{"class": "dark:text-gray-600"})
                    title = section.text.strip()
                    description = div.find('span',{"class": "text-sm dark:text-gray-600"}).text.strip()
                    link = div['href']
                    list_div.append({"title" : title, "description" : description, 'link': link, 'slug': filename})
                divs_name=soup.find_all('a', {"class":"announcement__container"})
                for div in divs_name:
                    title = div.find('span',{"class": "text-xs text-white"}).text.strip()
                    description = ''
                    link = div['href']
                    appender(title,'incransom',description,'',date,link)
                file.close()
        #except:
        #    errlog('incransom: ' + 'parsing fail')
        #    pass
