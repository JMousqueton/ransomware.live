
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
            if filename.startswith('medusalocker-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                articles = soup.find_all('article')
                for article in articles:
                    # Extract the link
                    link = article.find('a')['href']

                    # Extract the title
                    title = article.find('h2', class_='entry-title').text.strip()

                    # Extract the content
                    content = article.find('div', class_='entry-content').text.strip()

                    # Extract the published date
                    date_element = article.find('time', class_='entry-date')
                    published_date = date_element['datetime']
                    # Format the published date
                    formatted_date = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S.%f")

                    appender(title, 'medusalocker', content,'',formatted_date, link)
                file.close()
        except:
            errlog('medusa locker : ' + 'parsing fail')
            pass
