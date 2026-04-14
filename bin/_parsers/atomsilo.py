"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |             |    X    |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys, json, re
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
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py', '')
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')

                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

                cards = soup.find_all('div', class_='leak-card')
                for card in cards:
                    title_tag = card.find('h3', class_='leak-title')
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)

                    domain_tag = card.find('span', class_='leak-domain')
                    website = domain_tag.get_text(strip=True).lower() if domain_tag else ''

                    goto = card.find('a', class_='goto')
                    post_url = ''
                    if goto and goto.get('href'):
                        post_url = base_url.rstrip('/') + '/' + goto['href'].lstrip('/')
                        post_url = post_url.replace('/leaks.html','')

                    appender(title.replace('|', '-'), group_name, '', website, '', post_url)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
