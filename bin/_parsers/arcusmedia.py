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

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('arcusmedia-'):
                html_doc=tmp_dir /  filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                articles = soup.find_all('article', class_='card')
                
                for article in articles:
                    title_tag = article.find('h2', class_='entry-title')
                    title = title_tag.text.strip() if title_tag else "No Title"

                    link_tag = title_tag.find('a') if title_tag else None
                    link = link_tag['href'] if link_tag else "No Link"

                    desc_tag = article.find('div', class_='entry-excerpt')
                    description = desc_tag.text.strip() if desc_tag else "No Description"

                    date_tag = article.find('time', class_='published')
                    date_str = date_tag['datetime'] if date_tag else "No Date"
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

                    # Clean up the input string to handle unexpected characters
                    cleaned_input_string = description.replace("\u2013", "-").replace("\u2026", "")

                    # Adjust the cleaning logic to handle concatenated domains
                    adjusted_cleaned_input_string = re.sub(r'([a-z]{2,})(www)', r'\1 www', cleaned_input_string)

                    # Refined regex pattern to capture separate domains
                    url_pattern = r'www\.[a-zA-Z0-9\-\.]+\.[a-z]{2,}'

                    # Find the first URL in the adjusted string
                    match = re.search(url_pattern, adjusted_cleaned_input_string)
                    website = match.group() if match else ""
                    appender(title,'arcusmedia',description,website,formatted_date,link)

                file.close()
        except Exception as e:
            errlog('Arcusmedia - parsing fail with error: ' + str(e) + 'in file:' + filename) 