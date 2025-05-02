"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('everest-'):
                html_doc = 'source/' + filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')
                # Find all victim entries
                for div in soup.find_all('div', class_='category-item js-open-chat'):
                    # Victim name
                    title_tag = div.find('div', class_='category-title')
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    # Published date
                    date_tag = div.find('div', class_='category-date')
                    published = ''
                    if date_tag:
                        date_str = date_tag.get_text(strip=True)
                        try:
                            # Try to parse date in format like '26 apr 2025'
                            published_dt = datetime.strptime(date_str, '%d %b %Y')
                            published = published_dt.strftime('%Y-%m-%d')
                        except Exception:
                            published = ''
                    url = div.get('data-translit')
                    # TODO: get base url from the groups.json for better maintainability
                    url = "http://ransomocmou6mnbquqz44ewosbkjk3o5qjsl3orawojexfook2j7esad.onion/news/" + url
                    # No description or website in this format
                    appender(title, 'everest','','',published, url)
                file.close()
        except:
            errlog("Everest - Failed during : " + filename)

