
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
import re
from datetime import datetime 
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('underground-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                url = find_slug_by_md5('underground', extract_md5_from_filename(html_doc))
                for package in soup.find_all('div', class_='block__package'):
                    link_tag = package.find('a')  
                    if link_tag and 'href' in link_tag.attrs:
                        link =  url + link_tag['href'].replace('package','packages')  
                    else:
                        link = ''
                    name = package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Name:').find_next('p').text.strip() if package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Name:') else 'Not found'
                    revenue = package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Revenue:').find_next('p').text.strip() if package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Revenue:') else 'Not found'
                    data_type = package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Type:').find_next('p').text.strip() if package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Type:') else 'Not found'
                    country = package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Сountry:').find_next('p').text.strip() if package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Сountry:') else 'Not found'
                    size = package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Size:').find_next('p').text.strip() if package.find(lambda tag: tag.name == 'span' and tag.text.strip() == 'Size:') else 'Not found'
                    date_span = package.find(lambda tag: tag.name == 'span' and 'Date:' in tag.text)
                    if date_span:
                        date_text = date_span.find_next('p').text.strip()
                        date_obj = datetime.strptime(date_text, '%m/%d/%Y %H:%M')
                        date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                        date = ''
                    description = "Revenue:" + revenue + " - Country :" + country 
                    appender(name,'underground',description,'',date,link.replace('/account_file_manager',''))                    
        except:
            errlog('Underground: ' + 'parsing fail')
            pass    