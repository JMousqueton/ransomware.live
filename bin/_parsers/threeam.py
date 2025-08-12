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
            if filename.startswith('threeam-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                post_divs = soup.find_all('div', class_='post')
                for post_div in post_divs:
                    post_title = post_div.find('div', class_='post-title-block').text.strip().replace('published files','').replace('...','').replace('NEW','')
                    victim  = post_title.split('\n')[0].strip()
                    description = post_div.find('div', class_='post-text').text.strip()
                    link = post_div.find('a', class_='post-more-link')
                    if link:
                        onclick_attr = link.get('onclick')
                        url = find_slug_by_md5('threeam', extract_md5_from_filename(str(html_doc)))
                        post = url +  onclick_attr.split("'")[1]
                    appender(
                            victim=victim,
                            group_name='threeam',
                            description=description,
                            website=victim,  # Optional, leave empty or populate if relevant data exists
                            published="",
                            post_url=post.replace('show-posts/',''),
                            country=""  # Optional, leave empty or populate if relevant data exists
                        )
                file.close()
        except Exception as e:
            errlog('Threeam - parsing fail with error: ' + str(e) + 'in file:' + filename) 

