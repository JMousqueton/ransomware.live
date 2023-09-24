"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |      X         |                  |    X     |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from urllib.parse import urlparse

def main():
    for filename in os.listdir('source'):
        #try:
           if filename.startswith('incransom-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('a', {"class":"flex flex-col justify-between w-full h-56 border-t-4 border-2 border-t-green-500 dark:border-gray-900 dark:border-t-green-500 rounded-[20px] bg-white dark:bg-navy-800"})
                for div in divs_name:
                    section = div.find('span',{"class": "dark:text-gray-600"})
                    title = section.text.strip()
                    description = div.find('span',{"class": "text-sm dark:text-gray-600"}).text.strip()
                    link = div['href']
                    site = find_slug_by_md5('incransom', extract_md5_from_filename(html_doc))
                    parsed_url = urlparse(site)
                    site = parsed_url.netloc
                    link = 'http://' +site + link
                    date_element = div.find('div', class_='flex items-center gap-2 text-gray-600 text-sm').text.strip()
                    date_obj = datetime.strptime(date_element, '%d.%m.%Y')
                    current_time = datetime.now().time()
                    updated_date_obj = datetime.combine(date_obj.date(), current_time)
                    date = updated_date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    #print(date + ' --> ' + title + ' - ' +  description + ' - ' + link)
                    appender(title,'incransom',description,'',date,link)
                divs_name=soup.find_all('a', {"class":"flex flex-col justify-between w-full h-56 border-t-4 border-2 border-t-red-500 dark:border-gray-900 dark:border-t-red-500 rounded-[20px] bg-white dark:bg-navy-800"})
                for div in divs_name:
                    section = div.find('span',{"class": "dark:text-gray-600"})
                    title = section.text.strip()
                    description = div.find('span',{"class": "text-sm dark:text-gray-600"}).text.strip()
                    link = div['href']
                    site = find_slug_by_md5('incransom', extract_md5_from_filename(html_doc))
                    parsed_url = urlparse(site)
                    site = parsed_url.netloc
                    link = 'http://' +site + link
                    date_element = div.find('div', class_='flex items-center gap-2 text-gray-600 text-sm').text.strip()
                    date_obj = datetime.strptime(date_element, '%d.%m.%Y')
                    current_time = datetime.now().time()
                    updated_date_obj = datetime.combine(date_obj.date(), current_time)
                    date = updated_date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    #print(date + ' --> ' + title + ' - ' +  description + ' - ' + link)
                    appender(title,'incransom',description,'',date,link)
                file.close()
        #except:
        #    errlog('incransom: ' + 'parsing fail')
        #    pass
