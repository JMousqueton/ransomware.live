"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('0mega-'):
                html_doc=tmp_dir /  filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                rows = soup.select('.datatable tr.trow') #[1:]
                for row in rows:
                    columns = row.find_all('td')
                    title = columns[0].get_text(strip=True)
                    last_updated_date_str = columns[4].get_text(strip=True)
                    pubdate = datetime.strptime(last_updated_date_str, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S.%f")
                    description = columns[2].get_text(strip=True)
                    link = columns[5].find('a')['href']
                    link = find_slug_by_md5('0mega', extract_md5_from_filename(Path(html_doc).name)) +str(link)
                    appender(title, '0mega', description,"",pubdate,link)
                file.close()
        except Exception as e:
            print('0mega - parsing fail with error: ' + str(e) + 'in file:' + filename) 
