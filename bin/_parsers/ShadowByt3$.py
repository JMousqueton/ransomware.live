"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |             |         |     X     |          |
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
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    ## Get the ransomware group name from the script name
    script_path = os.path.abspath(__file__)
    # If it's a symbolic link find the link source
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py', '')
    # else get the script name
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')
                file.close()

                # Only process the leaks page (contains the PUBLIC LEAKS header)
                if not soup.find('h1', string=lambda t: t and 'PUBLIC LEAKS' in t):
                    continue

                # Find the leaks table rows (skip header row)
                rows = soup.select('table tbody tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 4:
                        continue

                    name = cells[0].get_text(strip=True)
                    release_str = cells[3].get_text(strip=True)

                    # Parse release date
                    published = ''
                    try:
                        date_obj = datetime.strptime(release_str, '%Y-%m-%d %H:%M:%S')
                        published = date_obj.strftime(date_format)
                    except Exception:
                        published = ''

                    if name:
                        appender(name.replace('_LEAK.7z',''), group_name, description='File: '+name, website='', published=published, post_url='', country='')

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
