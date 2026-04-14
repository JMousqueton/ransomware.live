"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys, re
from bs4 import BeautifulSoup
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
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

                for post in soup.find_all('div', class_='post-card'):
                    title_tag = post.find('h3', class_='post-title')
                    if not title_tag:
                        continue
                    victim = title_tag.get_text(strip=True)

                    excerpt_tag = post.find('div', class_='post-excerpt')
                    description = excerpt_tag.get_text(strip=True) if excerpt_tag else ''

                    post_url = ''
                    onclick = post.get('onclick', '')
                    match = re.search(r"window\.location='([^']+)'", onclick)
                    if match:
                        post_url = base_url + match.group(1)

                    appender(victim, group_name, description, victim, '', post_url, '')
                    #print('victim',victim)
                    #print('DEsc.',description)
                    #print('post_url:',post_url)

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
