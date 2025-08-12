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
import pycountry

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
                for card in soup.find_all("div", class_="card-body project-box"):
                    title_tag = card.find("h3", class_="mt-0")
                    title_link_tag = title_tag.find("a") if title_tag else None
                    title = title_link_tag.text if title_link_tag else None
                    link = title_link_tag['href'] if title_link_tag and title_link_tag.has_attr('href') else None
                    
                    description_tag = card.find("p", class_="text-muted font-15")
                    description = description_tag.text.strip() if description_tag else None
                    link = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))) + '/blog/' + link
    
                    
                    '''
                    print('victim:', title)
                    print('description:', description)
                    print('post_url:', link)
                    '''

                    appender(
                        victim=title,
                        group_name=group_name,
                        description=description,
                        website="",  
                        published="",
                        post_url=link,
                    )
                    
                file.close()
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)