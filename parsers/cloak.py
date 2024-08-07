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
    for filename in os.listdir('source'):
        #try:
           if filename.startswith('cloak-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')

                main_items = soup.find_all('div', class_='main__items')
                for item in main_items:
                    victim = item.find('h2').get_text()
                    description = item.find('p', class_='main__country').get_text()
                    link_element = item.find('a', class_='main__link')
                    url = ''
                    if link_element is not None:
                        link = link_element['href'] 
                        if link_element:
                            url = find_slug_by_md5('cloak', extract_md5_from_filename(html_doc))
                            url =  url + link
                    appender(victim, 'cloak',description,'','',url)
                '''
                company_blocks = soup.find_all("div", class_="ann-block")

                # Define the current and target date formats
                current_format = "%b %d, %Y %I:%M %p"  # Adjust this based on the actual format in the HTML
                target_format = "%Y-%m-%d %H:%M:%S.000000"

                for block in company_blocks:
                    # Extract the company name
                    company_name = block.find("div", class_="a-b-n-name").text.strip()
                    
                    # Extract the company description
                    company_description = block.find("div", class_="a-b-text").get_text(separator=" ").strip().replace('|','-')
                    
                    # Extract the date string
                    date_str = block.find("div", class_="a-b-h-time").text.strip()

                    # Parse and reformat the date
                    date = datetime.strptime(date_str, current_format)
                    formatted_date = date.strftime(target_format)

                

                    #print(f"Date: {formatted_date}")
                    #print(f"Company Name: {company_name}")
                    #print(f"Description: {company_description}")
                    #print("-" * 50)  # Separator line
                    appender(company_name, 'cloak',company_description,'',formatted_date,'')
                '''
                file.close()
        #except:
        #    errlog('cloak: ' + 'parsing fail')
        #    pass
