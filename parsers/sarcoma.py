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
                #divs=soup.find_all('div', {"class": "modal fade"})
                divs = soup.find_all('div', class_='modal-content sg-form')
                for div in divs:
                    victim = div.find('h5').text.strip()
                    if victim not in ('Contacts', 'About Us'):
                        description = div.find('pre', {"class": "text-break mb-2"}).text.strip()
                        
                        # Find the parent element containing GEO, Leak size, Contains
                        details = div.find_all('div')
                        geo = 'N/A'
                        leak_size = 'N/A'
                        contains = 'N/A'
                        
                        for detail in details:
                            if detail.text.startswith('GEO:'):
                                geo = detail.text.split(':')[-1].strip()
                            elif detail.text.startswith('Leak size:'):
                                leak_size = detail.text.split(':')[-1].strip()
                            elif detail.text.startswith('Contains:'):
                                contains = detail.text.split(':')[-1].strip()
                        
                        description = description + "Geo: " + geo + " - Leak size: " + leak_size + " - Contains: " + contains  

                        # Print extracted information
                        #print(f"Victim: {victim}")
                        #print(f"Description: {description}")
                        #print("-" * 40)  # Separator for readability


                        appender(victim, group_name, description)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)