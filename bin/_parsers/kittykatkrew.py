"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, datetime, sys
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

                cards = soup.find_all('a', class_='card')
                for card in cards:
                    title = card.find('div', class_='card-title').get_text(strip=True)

                    post_path = card.get('href', '')
                    post_url = base_url + post_path

                    body_div = card.find('div', class_='card-body')
                    description = body_div.get_text(strip=True) if body_div else ''

                    # Countdown deadline → include in description if present
                    countdown_tag = card.find('span', attrs={'data-countdown': True})
                    if countdown_tag:
                        deadline = countdown_tag['data-countdown']
                        description = (description + f' Deadline: {deadline}').strip()

                    # Status
                    status_div = card.find('div', class_=lambda c: c and 'card-status' in c)
                    if status_div:
                        status_text = status_div.get_text(strip=True)
                        description = (description + f' Status: {status_text}').strip()

                    # Published date (first <span> in card-footer)
                    footer = card.find('div', class_='card-footer')
                    published = ''
                    if footer:
                        date_span = footer.find('span')
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                            try:
                                date_obj = datetime.strptime(date_text, '%Y-%m-%d')
                                published = date_obj.strftime('%Y-%m-%d 00:00:00.000000')
                            except ValueError:
                                published = date_text

                    if title != "Operations begin.":
                        appender(
                            victim=title,
                            group_name=group_name,
                            description=description,
                            website='',
                            published=published,
                            post_url=post_url,
                            country=''
                        )
                    '''
                        print('victim:', title)
                        print('desc.:', description)
                        print('published:', published)
                        print('post_url:', post_url)
                        print('---')
                    '''
        except Exception as e:
            errlog(f'{group_name}: parsing fail with error: {str(e)} on file {filename}')
