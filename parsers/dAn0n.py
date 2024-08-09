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
            if filename.startswith('dAn0n-'):
                print('*')
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
                    try:
                        link = card.find("a", class_="btn btn-dark btn-sm")["href"]
                        link=find_slug_by_md5('dAn0n', extract_md5_from_filename(html_doc)) +  link
                    except:
                        link='' 
                    appender(title,'dAn0n', description, '',formatted_date,link)
        except Exception as e:
            errlog('dAn0n - parsing fail with error: ' + str(e) + ' victim: '+ title)
