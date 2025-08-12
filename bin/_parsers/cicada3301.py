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
        try:
            if filename.startswith(group_name+'-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                company_cards = soup.find_all('div', class_='w-full sm:w-1/2 md:w-1/2 lg:w-1/3 xl:w-1/3 px-6 mb-12')
                for card in company_cards:
                    name = card.find('h2', class_='font-bold').get_text(strip=True)
                    website = card.find('a', class_='text-blue-400')['href'].replace('https://','').replace('http://','')
                    size_data = card.find('span', string='size data:').find_next_sibling('span').get_text(strip=True)
                    attachments = card.find('span', string='Attachments:').find_next_sibling('span').get_text(strip=True)
                    status = card.find('span', string='Status:').find_next_sibling('span').get_text(strip=True)
                    created_raw = card.find('span', string='Created:').find_next_sibling('span').get_text(strip=True)
                    created_date = datetime.strptime(created_raw, '%B %d, %Y')  # Parse from 'December 15, 2024'
                    created_formatted = created_date.isoformat(sep=' ', timespec='microseconds')  # Format as '2023-06-05 11:27:26.515738'
                    view_post_tag = card.find('a', class_='inline-flex', href=True)
                    view_post_link = view_post_tag['href'] if view_post_tag else None
                    link = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))) +  view_post_link
                    description = f"Status: {status} - Size Data: {size_data}"
                    #appender(name, group_name, description,website,created_formatted,link)
                    appender(
                        victim=name,
                        group_name=group_name,
                        description=description,
                        website=website,  # Optional, leave empty or populate if relevant data exists
                        published=created_formatted,
                        post_url=link,
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)