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

# Define a function to convert the date format
def convert_date_format(input_date):
    # Split the input date string to extract the month, day, and year
    parts = input_date.split(', ')
    if len(parts) > 2:
        date_str = parts[1] + ', ' + parts[2]  # Extract "April 25, 2023" part
        # Parse the date using datetime
        parsed_date = datetime.strptime(date_str, '%B %d, %Y')
        # Format the date in the desired format
        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S.%f')
        return formatted_date
    return input_date  # Return the input date if the 

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('ciphbit-'):
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                h2_elements = soup.find_all('h2')
                for h2 in h2_elements:
                    victim = h2.get_text().replace('\n','')
                    a_element = h2.find_next('a')
                    website = a_element.get('href') if a_element else ''
                    h5_element = h2.find_next('h5')
                    # Get the text within the <h5> element as the published date
                    try:
                        published_date = h5_element.get_text() if h5_element else ''
                        published = convert_date_format(published_date)
                    except: 
                        published = ''
                    p_elements = h2.find_parent().find_all('p')
                    description = ' '.join(p.get_text() for p in p_elements)
                    appender(
                        victim=victim,
                        group_name='ciphbit',
                        description=description,
                        website=website,  # Optional, leave empty or populate if relevant data exists
                        published=published,
                        post_url="",
                        country=""  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog('ciphbit - parsing fail with error: ' + str(e) + 'in file:' + filename) 
