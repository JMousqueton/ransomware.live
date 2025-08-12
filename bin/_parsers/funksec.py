"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
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
        #try:
            if filename.startswith(group_name+'-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                #products_container = soup.find('main', class_='products-container')
                #for product in products_container.find_all('a', class_='product-card'):
                for product in soup.find_all("a", class_="product-card"):
                    remove_list = [
                        ' Database', ' database', ' breach', ' V1', 
                        ' Breached soon', ' company', ' Breach', 
                        ' access', ' has been hacked', ' Full Data',
                        ' Ransom'
                    ]
                    victim_name = product.find('h2').get_text(strip=True)
                    for item in remove_list:
                        victim_name = victim_name.replace(item, '')
                    #victim_link = 'http://7ixfdvqb4eaju5lzj4gg76kwlrxg4ugqpuog5oqkkmgfyn33h527oyyd.onion/'+ product.get('href')
                    if product.get('href'):
                        victim_link = find_slug_by_md5('funksec', extract_md5_from_filename(str(html_doc))) + '/' + product.get('href')
                    else:
                        victim_link = ''
                    appender(victim_name,group_name,'','','',victim_link)
        #except Exception as e:
        #    errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)
