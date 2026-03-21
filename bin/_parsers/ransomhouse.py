"""
    ransomhouse parser — updated for React SPA frontend (2026-03)

    Site moved from JSON-in-<pre> to div.cls_record HTML structure.

    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, datetime, sys, re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import appender, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('ransomhouse-'):
                date_format = "%d/%m/%Y"
                desired_format = "%Y-%m-%d %H:%M:%S.%f"
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')

                onion_host = 'zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion'

                for record in soup.find_all('div', class_='cls_record'):
                    link_tag = record.find('a', href=True)
                    if not link_tag:
                        continue

                    # Victim name
                    name_div = record.find('div', class_='cls_recordTop')
                    title = name_div.get_text(strip=True) if name_div else None
                    if not title:
                        continue

                    # Website
                    url_div = record.find('div', class_='cls_recordMiddle')
                    website = url_div.get_text(strip=True) if url_div else ''

                    # Post URL
                    post_url = 'http://' + onion_host + link_tag['href']

                    # Action date from bottom elements
                    formated_date = ''
                    for elem in record.find_all('div', class_='cls_recordBottomElement'):
                        header = elem.find('div', class_='cls_headerSmall')
                        if header and 'Action date' in header.get_text():
                            date_div = elem.find_all('div')
                            if len(date_div) > 1:
                                try:
                                    datetime_obj = datetime.strptime(
                                        date_div[1].get_text(strip=True), date_format
                                    )
                                    formated_date = datetime_obj.strftime(desired_format)
                                except ValueError:
                                    pass
                            break

                    appender(title, 'ransomhouse', '', website, formated_date, post_url)

                file.close()
        except Exception as e:
            errlog(f'ransomhouse: parsing fail with error {e}')
