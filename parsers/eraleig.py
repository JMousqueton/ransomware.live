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
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('eraleig-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                segment_box = soup.find('div', class_='segment__box')
                for segment in segment_box.find_all('div', class_='segment published'):
                    post_url = find_slug_by_md5('eraleig', extract_md5_from_filename(html_doc)) + segment.get('onclick').split('=')[1].strip("'")+"="+segment.get('onclick').split('=')[2].strip("'") 
                    victim = segment.find('div', class_='segment__text__off').text.strip()
                    description = segment.find('div', class_='segment__text__dsc').text.strip()
                    date_text = segment.find('div', class_='segment__date__deadline').text.strip()
                    date_text = date_text.replace('UTC +0', '').strip()
                    date_obj = datetime.strptime(date_text, '%Y/%m/%d %H:%M:%S')
                    date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    appender(victim,'eraleig',description,'',date,post_url)
        except:
            errlog('Eraleig: ' + 'parsing fail')
            pass
