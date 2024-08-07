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
            if filename.startswith('arcusmedia-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                articles = soup.find_all('article', class_='card')
                
                for article in articles:
                    title_tag = article.find('h2', class_='entry-title')
                    title = title_tag.text.strip() if title_tag else "No Title"

                    link_tag = title_tag.find('a') if title_tag else None
                    link = link_tag['href'] if link_tag else "No Link"

                    desc_tag = article.find('div', class_='entry-excerpt')
                    description = desc_tag.text.strip() if desc_tag else "No Description"

                    date_tag = article.find('time', class_='published')
                    date_str = date_tag['datetime'] if date_tag else "No Date"
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

                    appender(title,'arcusmedia',description,'',formatted_date,link)

                file.close()
        except:
            errlog("Failed during : " + filename)