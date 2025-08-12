"""
    From Template v4 - 202412827
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys
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
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    # Extract the link
                    link_tag = card.find('a', class_='card-logo')
                    if link_tag:
                        link= find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))  + link_tag['href']  
                    else:
                        link = ''
                    
                    # Extract the title
                    title_tag = card.find('div', class_='cart-text card-title')
                    title = title_tag.get_text(strip=True) 
                    
                
                    # Extract the date
                    date_tag = card.find("div", cds_text="caption")
                    if not date_tag:
                        date_tag = card.find("div", class_="card-text") 
                    if date_tag:
                        date_str = date_tag.get_text(strip=True) 
                    date_str = date_tag.get_text(strip=True) if date_tag else ""
                    formatted_date = ""
                    if date_str:
                            try:
                                parsed_date = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
                                formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                            except ValueError:
                                formatted_date = date_str  # Keep original if parsing fails
                    
                    # Extract the description
                    description_tag = card.find('div', class_='card-text card-description')
                    description = description_tag.get_text(strip=True) if description_tag else ''

                   
                    appender(title, group_name, description,'',formatted_date,link)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)