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
                victims_div = soup.find("div", class_="row bg-secondary p-3 rounded-4 roboto")
                for victim_div in victims_div.find_all("div", class_="col-sm-4 p-2"):
                    name_tag = victim_div.find("h5", class_="fw-bold mb-2")
                    victim = name_tag.get_text(strip=True) if name_tag else ""
                    description_tag = name_tag.find_next_sibling("h5") if name_tag else None
                    description = description_tag.get_text(strip=True) if description_tag else "N/A"
                    link_tag = victim_div.find("a", class_="btn btn-light fw-bold w-100")
                    post_url = link_tag["href"] if link_tag and link_tag.has_attr("href") else "N/A"
                
                    #appender(name, group_name, description,website,created_formatted,link)

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website='',  # Optional, leave empty or populate if relevant data exists
                        published='',
                        post_url=post_url,
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)