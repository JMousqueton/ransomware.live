"""
    From Template v2 - 20240526
    +------------------------------+------------------+----------+
    | Description | Published Date | Victim's Website | Post URL |
    +------------------------------+------------------+----------+
    |      X      |        X       |                  |     X    |
    +------------------------------+------------------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender 
from datetime import datetime

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
                articles = soup.find_all('article')
                for article in articles:
                    title_tag = article.find('h1')
                    link_tag = article.find('a', href=True)
                    summary_tag = article.find('p', class_='opacity-70')
                    tags = article.find_all('span', class_='inline-flex')
                    if title_tag and link_tag:
                        title = title_tag.get_text(strip=True)
                        link = link_tag['href']
                        summary = summary_tag.get_text(strip=True) if summary_tag else ""
                        tags_list = [tag.get_text(strip=True) for tag in tags]
                        tags_summary = ' '.join(tags_list)
                        full_summary = f"{summary} Tags: {tags_summary}" if tags_summary else summary

                        appender(title, group_name, full_summary,"","",link )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)