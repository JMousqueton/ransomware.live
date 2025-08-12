"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re
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
        #try:
            if filename.startswith(group_name+'-'):
                html_doc=tmp_dir / filename
                print('*** ', html_doc)
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for company in soup.find_all(class_='company-item'):
                    description = company.find(class_='name').text.strip()
                    victim = re.sub(r'\s*\(.*?\)', '', description)
                    if victim.startswith('Views:'):
                        victim = ''
                    print('victim:', victim)
                    url = company.find(class_='url').a['href']
                    url = re.sub(r'^https?://(www\.)?', '', url)
                    hacked_at = company.find(class_='hacked_at').find_all('div')[1].text.strip()
                    leak_at = company.find(class_='leak_at').find_all('div')[1].text.strip()
                    data_size = company.find(class_='data_size').find_all('div')[1].text.strip().replace('GB',' GB')
                    #country_img = company.find(class_='about_company').find('img')
                    #country = country_img['src'].split('/')[-1].split('.')[0].upper() if country_img else 'Unknown'
                    
                    extra_infos = { 'data_size': data_size }
                    appender(victim, group_name, description, url, hacked_at + " 00:00:00.000000", '', '', extra_infos)
        #except Exception as e:
        #    errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)