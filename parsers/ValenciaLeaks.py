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
                thread_boxes = soup.find_all('div', class_='thread-box')
                for i, box in enumerate(thread_boxes, start=1):
                    card_title = box.find('h5', class_='card-title').string if box.find('h5', class_='card-title') else "N/A"
                    time_left = box.find('p', class_='time-left').string if box.find('p', class_='time-left') else "N/A"
                    data_finaldate = box.get('data-finaldate', 'N/A')
                    data_leak = box.get('data-leak', 'N/A')
                    size = box.find('span', class_='price').string if box.find('span', class_='price') else "N/A"
                    view_link = box.find('a', class_='btn').get('href') if box.find('a', class_='btn') else "N/A"
                    link = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc)) + view_link
                    description = f"Data Exfiltrated : {size} - Leak Date : {data_finaldate}"
        

                    appender(card_title, group_name, description,"","",link )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
