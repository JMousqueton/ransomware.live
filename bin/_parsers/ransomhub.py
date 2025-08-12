"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, stdlog, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def convert_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return date_str

def extract_size(card):
    """Extracts the data size from the card's text content."""
    size_text = card.find('p').get_text(strip=True)
    match = re.search(r'Data Size:\s*([\d\.]+)\s*(GB|TB)', size_text, re.IGNORECASE)
    if match:
        size_value, size_unit = match.groups()
        return f"{size_value} {size_unit}"
    return ""


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('ransomhub-'):
                html_doc=tmp_dir /  filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    title_tag = card.find('div', class_='card-title').strong
                    title = title_tag.get_text(strip=True)
                    url = find_slug_by_md5('ransomhub', extract_md5_from_filename(Path(html_doc).name))
                    link = card.find_parent('a')['href']
                    post_date = convert_date(card.find('div', class_='card-footer').get_text(strip=True))
                    post_url= url + '/' + link
                    title = title.replace("<Taiwan>",'').replace("<Updated>","")
                    data_size = extract_size(card)
                    if data_size:
                        extra_infos = { 'data_size': data_size }
                    else:
                        extra_infos = ''
                    appender(title, 'ransomhub',"","",post_date,post_url,'',extra_infos)
                file.close()
        except Exception as e:
            errlog('ransomhub' + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
