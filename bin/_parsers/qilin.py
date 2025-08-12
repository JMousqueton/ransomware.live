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
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, "html.parser")
                ##divs_name = soup.find_all('div', {"class": "col-lg-4 col-sm-6 mb-4"})
                # Loop through each item box and extract the required information
                item_boxes = soup.find_all("div", class_="item_box")
                for box in item_boxes:
                    # Extract the victim name
                    name_tag = box.find("a", class_="item_box-title")
                    victim_name = name_tag.text.strip() 
                    # Extract the date
                    date_tags = box.find_all("div", class_="item_box-info__item d-flex align-items-center")
                    if len(date_tags) > 1:
                        raw_date = date_tags[1].text.strip()
                        try:
                            # Parse the date string
                            parsed_date = datetime.strptime(raw_date, "%b %d, %Y")
                            formatted_date = parsed_date.strftime(date_format)
                        except ValueError:
                            formatted_date = ""
                    else:
                        formatted_date = ""
                    
                    # Extract the URL
                    url_tag = box.find("a", class_="item_box-info__link")
                    url = url_tag['href'].strip() if url_tag else ""
                    # Remove the protocols
                    website = re.sub(r'^http[s]?://', '', url)
  
                    # Extract the description
                    description_tag = box.find("div", class_="item_box_text")
                    description = description_tag.text.strip() if description_tag else "N/A"
                    
                    # Extract the post URL
                    post_url_tag = box.find("a", class_="learn_more")
                    post_url = post_url_tag['href'].strip() 
                    if post_url:
                        site = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))
                        site = "http://ijzn3sicrcy7guixkzjkib4ukbiilwc3xhnmby4mcbccnsd7j2rekvqd.onion"
                        post_url = site + post_url
                    else:
                        post_url = ""
                    
                    appender(victim_name, group_name, description,website,formatted_date,post_url)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file:' + filename)

