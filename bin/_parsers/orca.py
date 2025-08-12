import os, datetime, sys, re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
import pycountry

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