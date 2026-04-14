"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |             |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys
from bs4 import BeautifulSoup
from datetime import datetime
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
            if filename.startswith('cipherforce-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                base_url = find_slug_by_md5('cipherforce', extract_md5_from_filename(str(html_doc)))

                for card in soup.find_all('div', class_='victim-card'):
                    name_tag = card.find('h3', class_='victim-name').find('a')
                    victim = name_tag.text.strip()
                    post_path = name_tag.get('href', '')
                    post_url = base_url + post_path if base_url else post_path

                    meta_items = card.find_all('span', class_='meta-item')
                    country = meta_items[1].text.strip() if len(meta_items) > 1 else ''

                    # Use deadline as published date only if it has already passed
                    published = ''
                    countdown = card.find('div', class_='countdown-timer')
                    if countdown and countdown.get('data-deadline'):
                        try:
                            deadline = datetime.strptime(countdown['data-deadline'], '%Y-%m-%dT%H:%M:%SZ')
                            if deadline <= datetime.utcnow():
                                published = deadline.strftime('%Y-%m-%d %H:%M:%S.%f')
                        except Exception:
                            pass

                    appender(victim, 'cipherforce', '', '', published, post_url, country)
                    '''
                    print('Victim:', victim)
                    print('Post URL:', post_url)
                    print('Published:', published)
                    print('Country:', country)
                    print('*' * 40)
                    '''

        except Exception as e:
            errlog('cipherforce - parsing fail with error: ' + str(e) + ' in file: ' + filename)
