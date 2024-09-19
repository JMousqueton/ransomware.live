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
                blog_cards = soup.find_all('div', class_='blog__card')
                for card in blog_cards:
                    # Extract title of the blog post
                    title = card.find('h2', class_='blog__card-top-info-title').get_text(strip=True)
                    
                    # Extract date of publication
                    publication_date = card.find('p', class_='blog__card-top-date').find('span').get_text(strip=True)
                    # print(f'Date of Publication: {publication_date}')
                    
                    # Extract description of the publication
                    description = card.find('div', class_='blog__card-description').find('p', class_='blog__card-description-text').get_text(strip=True)
                    
                    # Extract company URL if it exists
                    url_element = card.find('a', class_='blog__card-details-item-text --small-title --blog__card-details-item-text=;oml')
                    company_url = url_element['href'].replace('https://','') if url_element else ''

                     # Extract the main link
                    main_link = card.find('a', class_='blog__card-btn --button')['href']
                
                    if title != 'INTRODUCTION':
                        appender(title, group_name, description,company_url,"",main_link)

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)