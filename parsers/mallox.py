"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
from datetime import datetime

def convert_date_time_format(date_time_str):
    # Parse the original date and time string (assuming DD/MM/YYYY HH:MM format)
    original_format = '%d/%m/%Y %H:%M'
    parsed_datetime = datetime.strptime(date_time_str, original_format)
    
    # Format the datetime object to the desired output format
    # Adding microseconds (.191811) as a static value since it's not present in the original data
    output_format = '%Y-%m-%d %H:%M:%S.191811'
    return parsed_datetime.strftime(output_format)


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('mallox-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                # Loop through each card to extract the required information with improved error handling
                for card in cards:
                # Extract victim's name from the 'card-body' div
                    title = card.find('div', class_='card-body').find('div', class_='fs-3 fw-bold text-gray-900 mb-2').get_text(strip=True)
                    # Extract date and time from the 'card-toolbar' span
                    date_time = card.find('div', class_='card-toolbar').span.get_text(strip=True)
                    published = convert_date_time_format(date_time)
        
                    # Attempt to extract description from the 'text-gray-500' div, handling cases where it might not be present
                    description_div = card.find('div', class_='text-gray-500 fw-semibold fs-5 mt-1 mb-7')
                    description = description_div.get_text(strip=True) if description_div else "Description not available"

                    # Check for the "view" link in the 'card-body' div, handling cases where it might not be present
                    view_link_element = card.find('div', class_='card-body').find('a', href=True)
                    link = view_link_element['href'] if view_link_element else False
                    url = ''
                    if link:
                        try:
                            url = find_slug_by_md5('mallox', extract_md5_from_filename(html_doc)) + str(link)
                        except:
                            url = ''
                        
                    appender(title, 'mallox', description,"",published,url)
                file.close()
        except:
            errlog('mallox: ' + 'parsing fail')
            pass
