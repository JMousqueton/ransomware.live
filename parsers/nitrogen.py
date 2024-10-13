"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
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
                ##divs_name = soup.find_all('div', {"class": "col-lg-4 col-sm-6 mb-4"})
                for post in soup.find_all('div', class_='w3-container'):
                    company = {}

                    # Extract company name (inside <h3> tags)
                    company_name_tag = post.find('h3')
                    victim = company_name_tag.get_text(strip=True)

                    # Extract URL (inside <a> tags)
                    url_tag = post.find('a', href=True)
                    url = url_tag['href']

                    # Extract description (inside <p> tags, excluding the URL and READ MORE parts)
                    description_tag = post.find_all('p')
                    description_texts = [desc.get_text(strip=True) for desc in description_tag[1:-1]]  # Skip the last 'READ MORE' link
                    description = ' '.join(description_texts)

                    # Extract "READ MORE" link (usually the last <a> tag inside the section)
                    read_more_tag = post.find('a', text='READ MORE »')
                    link = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc)) + read_more_tag['href']

                    appender(victim, group_name, description,url,'',link)

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)