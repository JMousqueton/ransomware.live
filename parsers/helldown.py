
"""
    From Template v3.1 - 20240813
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,sys
from bs4 import BeautifulSoup
## Only if needed
## from datetime import datetime
## import re

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender, is_fqdn

def main():
    ## Define the date format 
    date_format = "%Y-%m-%d %H:%M:%S.%f"   
    ## Get the ransomware group name from the script name 
    group_name = __name__.split('.')[-1].replace("-api", "")
    for filename in os.listdir('source'):
        try:
            if filename.startswith(group_name+'-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')

                ### HERE GOES SPECIFIC CODE

                cards = soup.find_all('div', class_='card-container')
                for card in cards:
                    victim = card.find('div', class_='card-title').text
                    link = card.find('a')['href']
                    description = card.find('p', class_='card-summary').text
                    if is_fqdn(victim.replace('www.','')):
                        website=victim 
                    elif is_fqdn(description.replace('www.','')):
                         website=description
                    else:
                        website=''
                    #if description != "Here's something encrypted, password is required to continue reading.":
                    #    victim  = description 
                    post_url = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc)) + link
                    appender(victim, group_name, description, website,'',post_url )
                    
                ### END OF SPECIFIC CODE

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)