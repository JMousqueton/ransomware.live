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
from datetime import datetime, time
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# Define a function to convert the date format
def convert_date_format(input_date):
    # Split the input date string to extract the month, day, and year
    parts = input_date.split(', ')
    if len(parts) > 2:
        date_str = parts[1] + ', ' + parts[2]  # Extract "April 25, 2023" part
        # Parse the date using datetime
        parsed_date = datetime.strptime(date_str, '%B %d, %Y')
        # Format the date in the desired format
        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S.%f')
        return formatted_date
    return input_date  # Return the input date if the 

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('arkana-'):
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                posts = soup.select("article.post")
                for post in posts:
                    name = post.select_one('[data-post-card-title] a')
                    date_tag = post.find("time")
                    website = None

                    # Parse website from text block
                    content_block = post.find("p")
                    if content_block and "Website" in content_block.text:
                        lines = content_block.text.strip().splitlines()
                        for idx, line in enumerate(lines):
                            if "Website" in line and idx + 1 < len(lines):
                                website = lines[idx + 1].strip()

                    # Convert date to full timestamp with 00:00:00.000000
                    full_timestamp = None
                    if date_tag and date_tag.get("datetime"):
                        base_date = datetime.strptime(date_tag.get("datetime"), "%Y-%m-%d")
                        full_timestamp = datetime.combine(base_date, time(0, 0, 0, 0))
                    appender(
                        victim=name.text.strip() if name else None,
                        group_name='arkana',
                        description='',
                        website=website,  # Optional, leave empty or populate if relevant data exists
                        published=str(full_timestamp) if full_timestamp else None,
                        post_url="",
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog('Arkana - parsing fail with error: ' + str(e) + 'in file:' + filename) 
