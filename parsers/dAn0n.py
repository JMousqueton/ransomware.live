"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |      X         |                  |          |
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
            if filename.startswith('dAn0n-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                # Parse the HTML
                soup = BeautifulSoup(file, 'lxml')
                # Find all cards that contain victim information
                cards = soup.find_all('div', class_='card mb-3')
                # Extracting information from each card
                for card in cards:
                    title = card.find('h6', class_='card-title').get_text(strip=True)
                    date_str = card.find('p', class_='card-text h6').get_text(strip=True)
                    date = datetime.strptime(date_str, '%b %d, %Y')
                    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S.000000')
                    description = card.find('p', class_='card-text text-muted').text.strip() #[&]
                    link = card.find('a', class_='btn btn-primary')['href']
                    if link: 
                        link=find_slug_by_md5('dAn0n', extract_md5_from_filename(html_doc)) +  link
                    appender(title,'dAn0n', description, '',formatted_date,link)
        except Exception as e:
            errlog('dAn0n - parsing fail with error: ' + str(e))
