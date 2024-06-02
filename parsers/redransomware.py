
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('redransomware-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for card in soup.find_all('div', class_='card border border-warning'):
                    name = card.find('h4', class_='card-header').text.strip()
                    description = card.find('p', class_='card-text').text.strip()
                    date_str = card.find('div', class_='card-footer').text.strip()

                    # Convert the date string to a datetime object
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

                    # Format the datetime object to the desired format
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    appender(name, 'redransomware', description,"",formatted_date,"")
                file.close()
        except:
            errlog("Failed during : " + filename)
