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
                news_blocks = soup.find_all('div', class_='news__block chat__block')
                for block in news_blocks:
                    title = block.find('h4', class_='chat__block-title').text.strip()
                    published = block.find('p', class_='chat__block-date').find('span').text.strip()
                    description = block.find('p', class_='chat__block-descr').text.strip()
                    link = block.find('a', class_='button button-blue')['href']
                    date_obj =  datetime.strptime(published, '%d/%m/%Y')
                    published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                    
                    link = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc)).replace('/leaks','') + link
                    
                    appender(title, group_name, description,"",published,link)

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)