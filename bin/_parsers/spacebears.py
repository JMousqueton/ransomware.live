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
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('spacebears-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                company_blocks = soup.find_all('div', class_='companies-list__item')
                for block in company_blocks:
                    image_block = block.find('div', class_='image-block')
                    name_tag = block.find('div', class_='name').find('a')
                    victim = name_tag.text.strip()
                    post_url = name_tag['href']
                    description_tag = block.find('div', class_='text') #.find('p')
                    description = description_tag.text.strip() if description_tag else 'No description available'
                    description = description.replace('\n',' ')
                    
                    if image_block:
                        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        published_tag = image_block.find('p')
                        if published_tag and 'Published' in published_tag.text:
                            # Extract the number of days and calculate the publication date
                            days_ago_text = published_tag.text.strip()
                            days_ago = int(days_ago_text.split()[1])
                            publication_date = current_date - timedelta(days=days_ago)
                            date = publication_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                        else:
                            date = ''
                    words = description.split() 
                    website = words[-1]
                    appender(victim,'spacebears',description,website,date,post_url)
                file.close()
        except Exception as e:
            errlog("spacebears" + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)