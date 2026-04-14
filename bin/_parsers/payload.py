"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys, re, json
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
            if filename.startswith('payload-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')

                site_onion_url = find_slug_by_md5('payload', extract_md5_from_filename(str(html_doc)))

                cards = soup.find_all('a', class_='card-link')
                for card in cards:
                    article = card.find('article', class_='card')
                    if not article:
                        continue

                    # Extract title
                    title_div = article.find('div', class_='title')
                    if not title_div:
                        continue
                    title = title_div.get_text(strip=True)
                    if not title:
                        continue

                    # Extract post URL from the <a class="card-link"> href
                    post_url = ''
                    href = card.get('href', '')
                    if href:
                        post_url = site_onion_url + href

                    # Extract description from <pre class="body">
                    description = ''
                    pre = article.find('pre', class_='body')
                    if pre:
                        description = pre.get_text(strip=True).replace('\n', ' ')

                    # Extract data size from <span class="company-size">
                    data_size = ''
                    size_span = article.find('span', class_='company-size')
                    if size_span:
                        data_size = size_span.get_text(strip=True)

                    # Check if title looks like a domain (website)
                    website = ''
                    if re.match(r'^[\w.-]+\.\w{2,}$', title):
                        website = title

                    extra_infos = {}
                    if data_size:
                        extra_infos['data_size'] = data_size

                    appender(title, 'payload', description, website, '', post_url, '', extra_infos)
                    '''
                    print('victim:', title)
                    print('desc.:', description)
                    print('website:', website)
                    print('post:', post_url)
                    print('data_size:', data_size)
                    print('-' * 40)
                    '''
                file.close()
        except:
            errlog('payload : parsing fail')
