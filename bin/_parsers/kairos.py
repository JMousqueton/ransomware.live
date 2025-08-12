"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys
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
        try:
            if filename.startswith(group_name+'-'):
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                cards = soup.select('div.listing a.card')

                for card in cards:
                    # Extract link
                    link = card['href']
                    
                    # Extract title and split by '\'
                    title_text = card.select_one('.title').get_text(strip=True)
                    title_parts = title_text.split('\\')
                    
                    # Extract title and country
                    title = title_parts[0] if len(title_parts) > 0 else "Unknown"
                    country = title_parts[1] if len(title_parts) > 1 else "Unknown"
                    
                    # Extract description
                    desc = card.select_one('.desc').get_text(strip=True)
                    try:
                        description = country + ' - ' + desc
                    except:
                        description = desc
                    # Extract and format date
                    try:
                        date_str = card.select_one('.date').get_text(strip=True)
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
                        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                    except:
                        formatted_date = ''
                    # link= find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))#  + link
                    link = "http://nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad.onion" + link 
                    

                    appender(title, group_name, description,title,formatted_date,link )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
