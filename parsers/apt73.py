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
            if filename.startswith('apt73-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                segment_box = soup.find('div', class_='segment__box')
                for segment in segment_box.find_all('div', class_='segment'):
                    link = segment.get('onclick').split("'")[1] if segment.get('onclick') else None
                    victim = segment.find('div', class_='segment__text__off').text.strip() if segment.find('div', class_='segment__text__off') else None
                    post_url = 'http://wn6vonooq6fggjdgyocp7bioykmfjket7sbp47cwhgubvowwd7ws5pyd.onion' +  str(link)
                    description = segment.find('div', class_='segment__text__dsc').text.strip() if segment.find('div', class_='segment__text__dsc') else None
                    date_info = segment.find('div', class_='segment__date__deadline').text.strip() if segment.find('div', class_='segment__date__deadline') else None
                    date_text = date_info.replace('UTC +0', '').strip()
                    date_obj = datetime.strptime(date_text, '%Y/%m/%d %H:%M:%S')
                    date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    current_datetime = datetime.now()
                    if date_obj > current_datetime:
                        date = ''
                    appender(victim,'apt73',description,'',date,post_url)
        except:
            errlog('apt73: ' + 'parsing fail')
            pass
