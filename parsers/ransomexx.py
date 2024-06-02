
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |      X         |                 |     x    |
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
            if filename.startswith('ransomexx-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                # Find all div tags with class 'entry-summary' and itemprop 'text'
                # Find all articles which seems to contain the information needed
                articles = soup.find_all('article')
                # Iterate over each article and extract the required information
                for article in articles:
                    title = article.find('h2', class_='entry-title').text.strip()
                    date = article.find('time', class_='entry-date').get('datetime')
                    date = datetime.fromisoformat(date)  # Assuming the date is in ISO format
                    formatted_date = date.strftime("%Y-%m-%d %H:%M:%S.%f")
                    link = article.find('h2', class_='entry-title').find('a').get('href')
                    description = article.find('div', class_='entry-summary').text.strip().replace('\n',' ')
                    link = find_slug_by_md5('ransomexx', extract_md5_from_filename(html_doc)) +  link
                    appender(title,'ransomexx',description,'',formatted_date, link)
        except:
            errlog('ransomexx: ' + 'parsing fail')
            pass