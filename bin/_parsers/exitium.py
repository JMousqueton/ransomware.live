"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys
from urllib.parse import quote
from bs4 import BeautifulSoup
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('exitium-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')
                file.close()

                # Only process published cards (skip pending/coming-soon cards)
                cards = soup.find_all('div', class_='target-card clickable-card')
                for card in cards:
                    # Victim name
                    victim = card.get('data-title', '').strip()
                    if not victim:
                        continue

                    # Description
                    description = card.get('data-text', '').strip()

                    # Post URL - base URL from slug lookup with anchor to victim name
                    anchor = quote(victim, safe='')
                    post_url = find_slug_by_md5('exitium', extract_md5_from_filename(str(html_doc))) + '#' + anchor

                    appender(
                        victim=victim,
                        group_name='exitium',
                        description=description,
                        website='',
                        published='',
                        post_url=post_url,
                        country=''
                    )
                    '''
                    print('Victim:', victim)
                    print('Description:', description)
                    print('Post URL:', post_url)
                    print('---')
                    '''
        except Exception as e:
            errlog('exitium - parsing fail with error: ' + str(e) + ' in file: ' + filename)
