"""
    ransomhouse parser — JSON-in-<pre> format

    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, json
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

                with open(html_doc, 'r') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                onion_host = 'zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion'

                pre = soup.find('pre')
                if not pre:
                    errlog(f'ransomhouse: no <pre> tag found in {filename}')
                    continue

                data = json.loads(pre.get_text())

                for record in data.get('data', []):
                    title = record.get('header', '')
                    if not title or record.get('display') == 'animated':
                        continue

                    website = record.get('url', '')
                    description = record.get('info', '')

                    content_file = record.get('content', '')
                    post_url = f'http://{onion_host}/{content_file}' if content_file else ''

                    formated_date = ''
                    action_date = record.get('actionDate', '')
                    if action_date:
                        try:
                            datetime_obj = datetime.strptime(action_date, date_format)
                            formated_date = datetime_obj.strftime(desired_format)
                        except ValueError:
                            pass

                    appender(title, 'ransomhouse', description, website, formated_date, post_url)
                    #print('title:', title)
                    #print('Desc.', description)
                    #print('website:', website)
                    #print('date:', formated_date)
                    #print('*' * 40)

        except Exception as e:
            errlog(f'ransomhouse: parsing fail with error {e}')
