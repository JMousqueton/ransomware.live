"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender
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

    for filename in os.listdir('source'):
        try:
            if filename.startswith(group_name+'-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='cls_record card')
                for post in soup.select('.post-head'):
                    title = post.select_one('.post-title').get_text(strip=True)
    
                    # Skip titles that are only question marks
                    if all(char == '?' for char in title):
                        continue

                    date_raw = post.select_one('.timer').get_text(strip=True)
                    summary = post.select_one('.post-block-text').get_text(strip=True)

                    # Convert the date format to "YYYY-MM-DD HH:MM:SS.ffffff"
                    try:
                        date = datetime.strptime(date_raw, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title, group_name, summary,"",date)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)