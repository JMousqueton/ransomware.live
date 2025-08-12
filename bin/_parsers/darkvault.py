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
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('darkvault-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                post_blocks = soup.find_all("div", class_="post-block")
                for post_block in post_blocks:
                    # Extract the victim's name (post title)
                    post_title = post_block.find("div", class_="post-title").get_text(strip=True)  
                    
                    # Extract the description
                    description = post_block.find("div", class_="post-block-text").get_text(strip=True)
                    
                    # Extract the published date
                    # Extract the published date and convert it
                    published_text = post_block.find("div", class_="updated-post-date").get_text(strip=True).replace('Posted: ', '')
                    published_date = datetime.strptime(published_text, "%d %B, %Y")  # Parse the date
                    published = published_date.strftime("%Y-%m-%d 00:00:00.000000")  # Format the date
                    
                    # Extract the 'onclick' attribute to get the post URL part
                    onclick_attr = post_block.get("onclick")
                    post_url_part = onclick_attr.split("'")[1] if onclick_attr else ""
                    post_url = f"http://mdhby62yvvg6sd5jmx5gsyucs7ynb5j45lvvdh4dsymg43puitu7tfid.onion/{post_url_part}" if post_url_part else "URL not available"

                    appender(
                        victim=post_title,
                        group_name='darkvault',
                        description=description,
                        website='',  # Optional, leave empty or populate if relevant data exists
                        published=published,
                        post_url=post_url,
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog('darkvault - parsing fail with error: ' + str(e) + 'in file:' + filename) 
