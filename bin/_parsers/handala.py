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
            if filename.startswith('handala-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                posts = soup.find_all('li', class_='wp-block-post')
                for post in posts:
                    victim = post.find('h2', class_='wp-block-post-title').text.strip().replace(' Hacked','').replace('Zionists ','').replace('Zionist ','').replace(' Sensitive Leak','')
                    date_str = post.find('div', class_='wp-block-post-date').time['datetime']
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S.%f')
                    description = post.find('div', class_='wp-block-post-excerpt').text.strip()
                    link = post.find('h2', class_='wp-block-post-title').a['href']
                    if victim not in ["New Telegram Channel", "Official Statement from Handala"]:
                        appender(
                            victim=victim,
                            group_name='handala',
                            description=description,
                            website="",  # Optional, leave empty or populate if relevant data exists
                            published=date,
                            post_url=link,
                            country=""  # Optional, leave empty or populate if relevant data exists
                        )
                    #appender(victim,'handala',description,'',date,link)
                file.close()
        except Exception as e:
            errlog('handala - parsing fail with error: ' + str(e))
