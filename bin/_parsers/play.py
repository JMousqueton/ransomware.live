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
            if filename.startswith('play-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('th', {"class": "News"})
                for div in divs_name:
                    title = div.next_element.strip()
                    description = div.find('i', {'class': 'location'}).next_sibling.strip()
                    website = div.find('i', {'class': 'link'}).next_sibling.strip()
                    post_url = find_slug_by_md5('play', extract_md5_from_filename(str(html_doc))) + '/topic.php?id='+div['onclick'].split("'")[1] 
                    post_url = post_url.replace('//topic','/topic')
                    added_date = None
                    div_text = div.find_next('div', {'style': 'line-height: 1.70;'}).get_text()
                    if 'added:' in div_text:
                        added_date = div_text.split('added:')[1].split('publication date:')[0].strip()
                        now = datetime.now()
                        added_date = f"{added_date} {now.strftime('%H:%M:%S.%f')}"
                    appender(
                        victim=title,
                        group_name='play',
                        description=description,
                        website=website,  # Optional, leave empty or populate if relevant data exists
                        published=added_date,
                        post_url=post_url,
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog(f'play - parsing fail with error: {str(e)} in file {html_doc}')