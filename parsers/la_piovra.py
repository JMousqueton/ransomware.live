
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
from sharedutils import errlog
from parse import appender
import re
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('la_piovra-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs=soup.find_all('article')
                for article in divs:
                    # Extract the title
                    title = article.find('h2', class_='entry-title').text.strip()

                    # Extract the URL
                    url = article.find('h2', class_='entry-title').a['href']

                    # Extract the datetime
                    # Extract the datetime
                    datetime_str = article.find('time', class_='entry-date')['datetime']
                    datetime_obj = datetime.fromisoformat(datetime_str)
                    published = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

                    description = article.find('div',{"class" : "entry-content"}).text.strip()

                    appender(title, 'la_piovra', description,"",published,url)

                file.close()
        except:
            errlog('la_piovra : ' + 'parsing fail')
            pass
