"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys, json
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
                pre_tag = soup.find("pre")
                if pre_tag:
                    json_text = pre_tag.text
                    json_data = json.loads(json_text)  # Convert string to JSON object
                    for entry in json_data:
                        """
                        print("ID:", entry.get("id", "N/A"))
                        print("Name:", entry.get("name", "N/A"))
                        print("Domain:", entry.get("domain", "N/A"))
                        print("Deadline:", entry.get("deadline", "N/A"))
                        print("Description:", entry.get("cardDescription", "N/A"))
                        print("Total Size:", entry.get("totalSize", "N/A"))
                        print("Ransom Amount:", entry.get("ransom", "N/A"))
                        print("Created At:", entry.get("created_at", "N/A"))
                        print("Logo:", entry.get("logo", "N/A"))
                        print("Images:", ", ".join(entry.get("images", [])))
                        print("Download Links:", entry.get("downloadLinks", "N/A"))
                        print("-" * 40)
                        """
                        appender(entry.get("name", ""), group_name, entry.get("cardDescription", "N/A"),entry.get("domain", ""),entry.get("created_at")+".000000",entry.get("downloadLinks", "N/A"))
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)