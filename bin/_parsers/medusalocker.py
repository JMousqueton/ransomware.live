"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('medusalocker-'):
                html_doc= tmp_dir / filename
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
