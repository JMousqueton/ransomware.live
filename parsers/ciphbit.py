
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename, remove_multiple_spaces
from parse import appender
from datetime import datetime

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
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ciphbit-'):
                html_doc='source/'+filename
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
                    description = description.replace('\n','')
                    appender(remove_multiple_spaces(victim), 'ciphbit', remove_multiple_spaces(description),website,published)
                file.close()
        except:
            errlog("Failed during : " + filename)
