"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, datetime, sys, re
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
            if filename.startswith('blackwater-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    title = card.find('h5', class_='card-title')
                    if not title:
                        continue
                    title = title.text.strip()

                    # Date: "Publicated at 2026-03-20 10:20:42"
                    published = ''
                    date_tag = card.find('p', class_='card-text text-muted')
                    if date_tag:
                        date_str = date_tag.text.strip().replace('Publicated at ', '')
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            published = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                        except:
                            published = ''

                    # Description: second p.card-text.text-muted (the one with style)
                    description = ''
                    desc_tags = card.find_all('p', class_='card-text text-muted')
                    if len(desc_tags) > 1:
                        description = desc_tags[1].text.strip()

                    # Post URL: /blog?uuid=...
                    post_url = ''
                    link_tag = card.find('a', class_='btn')
                    if link_tag:
                        href = link_tag.get('href', '')
                        base = find_slug_by_md5('blackwater', extract_md5_from_filename(str(html_doc)))
                        post_url = base + href if base else href

                    appender(title, 'blackwater', description, '', published, post_url)

                file.close()
        except Exception as e:
            errlog('blackwater - parsing fail with error: ' + str(e) + ' in file: ' + filename)
