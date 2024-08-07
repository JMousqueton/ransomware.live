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
            if filename.startswith('cyclops-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                # Find all the <div> elements with class "block-content"
                post_divs = soup.find_all('div', class_='block-content')

                # Iterate over each <div> element to extract the desired information
                for div in post_divs:
                    # Extract the title
                    title = div.find('h2').get_text(strip=True)

                    # Extract the date string
                    date_string = div.find('p', class_='fs-sm').find('span', class_='text-primary').next_sibling.strip()
    
                    # Convert the date string to a datetime object
                    date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    
                    # Format the date in the desired format
                    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S.%f')

                    # Extract the description
                    description = div.find("strong").text.strip().replace('\t', ' ').replace('\n', ' ')

                    appender(title, 'cyclops',description,'',formatted_date)
                file.close()
        #except:
        #    errlog('cyclops : ' + 'parsing fail')
        #    pass
