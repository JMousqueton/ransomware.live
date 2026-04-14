"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys
import pycountry
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

                for post in soup.find_all('div', class_='blog-item'):
                    title_tag = post.find('div', class_='blog-item-title')
                    if not title_tag:
                        continue
                    victim = title_tag.get_text(strip=True)

                    website_div = post.find('div', class_='blog-item-info-website')
                    website = ''
                    if website_div:
                        a_tag = website_div.find('a', href=True)
                        if a_tag:
                            website = a_tag['href']

                    location_div = post.find('div', class_='blog-item-info-location')
                    country = ''
                    if location_div:
                        location_text = location_div.get_text(strip=True)
                        last_part = location_text.split(',')[-1].strip()
                        try:
                            country = pycountry.countries.lookup(last_part).alpha_2
                        except LookupError:
                            country = last_part

                    description_div = post.find('div', class_='blog-item-description')
                    description = description_div.get_text(strip=True) if description_div else ''

                    button_div = post.find('div', class_='blog-item-button')
                    post_url = ''
                    if button_div:
                        link_tag = button_div.find('a', href=True)
                        if link_tag:
                            post_url = base_url + link_tag['href']

                    appender(victim, group_name, description, website, '', post_url, country)
                    """
                    print('victim:',victim)
                    print('desc.:',description)
                    print('web:',website)
                    print('url:',post_url)
                    print('country:',country)
                    print('*'*40)
                    """
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
