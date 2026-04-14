"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |             |         |           |     X    |
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

def clean_title(title):
    title = re.sub(r'\d+GB', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\d+M\s+records', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(.*?\)', '', title)
    title = re.sub(r'\bExtranet\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\bInternal\s+Data\b', '', title, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', title).strip()

def main():

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

                items = soup.find_all('div', class_='target-card')
                for item in items:
                    # Skip pending/awaiting upload entries
                    if item.find('span', class_='status-pending'):
                        continue

                    title = clean_title(item.get('data-name', ''))
                    published = item.get('data-date', '')

                    # Extract description from leak-date text after the " | " separator
                    description = ""
                    leak_date_div = item.find('div', class_='leak-date')
                    if leak_date_div:
                        leak_text = leak_date_div.get_text(strip=True)
                        if ' | ' in leak_text:
                            description = leak_text.split(' | ', 1)[1].strip()

                    # First mirror link as post_url
                    post_url = ""
                    first_link = item.find('a', class_='m-link')
                    if first_link:
                        post_url = first_link.get('href', '')

                    appender(
                        victim=title,
                        group_name=group_name,
                        description=description,
                        website="",
                        published=published,
                        post_url="",
                        country=""
                    )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
