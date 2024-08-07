"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('blackbyte-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('table', {"class": "table table-bordered table-content"})
                # <table class="table table-bordered table-content ">
                for div in divs_name:
                    title = div.find('h1').text.strip()
                    description = div.find('p').text.strip().replace("\n", "")
                    website = div.find('a')
                    website = website.attrs['href']
                    appender(title, 'blackbyte', description,website)
                file.close()
        except:
                pass
        try:
            if filename.startswith('blackbyte-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                tables = soup.find_all('table', class_='table')

                # Extract captions and last dates
                for table in tables:
                   caption = table.find('caption', class_='target-name').text
                   rows = table.find('tbody').find_all('tr')
                   last_date = rows[-1].find('td').text
                   #print(f"Table Caption: {caption}")
                   #print(f"Last Date: {last_date}")
                   last_date = datetime.strptime(last_date, '%Y-%m-%d %H:%M')
                   published = last_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                   appender(caption, 'blackbyte', '','',published)
        except Exception as e:
            #errlog('blackbyte: ' + 'parsing fail: '  + str(e))
            pass
