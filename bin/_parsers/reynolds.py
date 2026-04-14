"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys, re
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
            if filename.startswith('reynolds-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')

                site_onion_url = find_slug_by_md5('reynolds', extract_md5_from_filename(str(html_doc)))

                sections = soup.find_all('section', class_='post-item')
                for section in sections:
                    # Extract title (domain name used as victim name)
                    title_tag = section.find('h2', class_='post-title')
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    if not title:
                        continue

                    # Extract post URL
                    post_url = ''
                    link = title_tag.find_parent('a', href=True)
                    if link:
                        post_url = link['href']

                    # Website from title (title is the domain)
                    website = ''
                    if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', title):
                        website = 'https://' + title

                    # Extract description
                    description = ''
                    abstract_div = section.find('div', class_='post-abstract')
                    if abstract_div:
                        p_tag = abstract_div.find('p')
                        if p_tag:
                            description = p_tag.get_text(strip=True).replace('\n', ' ')

                    # Extract published date
                    published = ''
                    post_info = section.find('div', class_='post-info')
                    if post_info:
                        date_span = post_info.find('span')
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                            try:
                                dt = datetime.strptime(date_text, '%Y-%m-%d')
                                published = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                published = ''

                    appender(title, 'reynolds', description, website, published, post_url)

                file.close()
        except:
            errlog('reynolds : parsing fail')
