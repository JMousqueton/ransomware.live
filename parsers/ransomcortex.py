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
                posts = soup.find_all('article')
                for post in posts:
                    # Extract title
                    title_tag = post.find('h2', class_='entry-title')
                    title = title_tag.text.strip() if title_tag else "No Title"
                    
                    # Extract description
                    description_tag = post.find('div', class_='post-content')
                    description = description_tag.text.strip() if description_tag else "No Description"
                    
                    # Extract link
                    link_tag = title_tag.find('a') if title_tag else None
                    link = link_tag['href'] if link_tag and link_tag.has_attr('href') else "No Link"
                    appender(title, group_name, description,"","",link)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)