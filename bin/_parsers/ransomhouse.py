"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re, json
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, stdlog, errlog
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
                html_doc= tmp_dir / filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart= soup.pre.contents 
                data = json.loads(jsonpart[0]) 
                for element in data['data']:
                    title = element['header']
                    link = element['id']
                    url = 'zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid'
                    post_url = 'http://' + url + '.onion/r/' + link
                    website = element['url']
                    try:
                        date_string = element['actionDate']
                        datetime_obj = datetime.strptime(date_string, date_format)
                        formated_date = datetime_obj.strftime(desired_format)
                    except:
                        formated_date = ''
                    description = re.sub(r'<[^>]*>', '',element['info'])
                    appender(title, 'ransomhouse', description,website,formated_date,post_url)
                file.close()
        except Exception as e:
            errlog(f'ransomhouse: parsing fail with error {e}')