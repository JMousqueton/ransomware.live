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
        try:
           if filename.startswith('incransom-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                items = soup.find_all('div', {"class": "mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"})
                for item in items:
                    title_element = item.find('span', class_='dark:text-gray-600')
                    title = title_element.get_text()
                    url_element = item.find('a', href=True)
                    url = url_element['href']
                    description_element = item.find('div', class_='flex w-full h-full p-2')
                    description = description_element.get_text()
                    date_element = item.find('div', class_='flex items-center gap-2 text-gray-600 text-sm').text
                    date_obj = datetime.strptime(date_element, '%d.%m.%Y')
                    current_time = datetime.now().time()
                    updated_date_obj = datetime.combine(date_obj.date(), current_time)
                    formatted_date = updated_date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    site = find_slug_by_md5('incransom', extract_md5_from_filename(html_doc))
                    parsed_url = urlparse(site)
                    site = parsed_url.netloc
                    appender(title, 'incransom',description.replace('\n',' '),'','http://'+formatted_date,site+url)
                file.close()
        except:
            errlog('incransom: ' + 'parsing fail')
            pass
