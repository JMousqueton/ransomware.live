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
    # Define the date format to convert to
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
        group_name = original_name.replace('.py','')
    # else get the script name 
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py','')

    for filename in os.listdir(tmp_dir):
        if filename.startswith(group_name+'-'):
            html_doc=tmp_dir / filename
            file=open(html_doc,'r')
            soup = BeautifulSoup(file, "html.parser")
            breaches = soup.find('ol').find_all('li')
            for breach in breaches:
                try:
                    title_tag = breach.find('h4').find('a')
                    title = title_tag.text.strip()
                    link = title_tag.get('href')

                    description = desc_tag = breach.find('p').text.strip()

                    # Extracting leak size
                    leak_match = re.search(r'Leak size:\s*([\d\.]+)\s*(GB|MB|TB)', description, re.IGNORECASE)
                    if leak_match:
                        size  = f"{leak_match.group(1)} {leak_match.group(2)}"
                        extra_infos = { 'data_size': size }
                    else:
                        extra_infos = ''  
                        
                    # Extracting date
                    date_tag = breach.find_all('b')
                    for tag in date_tag:
                        if 'Date:' in tag.text:
                            parsed_date = tag.next_sibling.strip() if tag.next_sibling else ""
                            parsed_date = datetime.strptime(parsed_date, "%a %d %B %Y")
                            formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                            break
                                   
                        
                    # Extract country from tags
                    country_tags = breach.find('em').find_all('a')
                    countries = ', '.join(tag.text.strip('# ') for tag in country_tags)
                    appender(title, group_name, description, '', formatted_date, link,'',extra_infos)
                except Exception as e:
                    errlog(f"{group_name} - entry parse fail: {e} in file: {filename}")
