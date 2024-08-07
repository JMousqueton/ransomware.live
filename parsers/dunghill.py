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

# Helper function to extract the text following a specific label
def extract_label_text(p_elements, label):
    for p in p_elements:
        if label in p.text:
            return p.text.replace(label, '').strip()
    return None

# Helper function to extract description text from <p> tags containing <strong>
def extract_raw(p_elements):
    for p in p_elements:
        if p.find('strong'):
            return p.text.strip()
    return None

def extract_description(p_elements):
    strong_p_tags = [p for p in p_elements if p.find('strong')]
    if len(strong_p_tags) > 1:
        return strong_p_tags[1].text.strip()
    return None

def convert_date(date_str):
    date_obj = datetime.strptime(date_str, '%d.%m.%Y')
    return date_obj.strftime('%Y-%m-%d 00:00:00.000000')


# Helper function to extract the website URL from the description
def extract_website(description):
    lines = description.split('\n')
    if len(lines) > 1:
        return lines[1].strip()
    return None

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
                custom_containers = soup.find_all('div', class_='custom-container')
                for container in custom_containers:
                    title = container.find('div', class_='ibody_title').text.strip()
                    p_elements = container.find_all('p')
                    date = extract_label_text(p_elements, 'Date:')
                    published = convert_date(date)
                    raw = extract_raw(p_elements)
                    description = extract_description(p_elements)
                    read_more_link = container.find('a', text='Read More')['href']
                    url = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc)) + '/' + read_more_link
                    website = extract_website(raw)
                    appender(title, group_name, description,website,published,url )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
