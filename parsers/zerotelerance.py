"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
import datetime
import re

# Function to parse and format the date
def parse_and_format_date(date_str):
    # Parsing the date assuming the format is like 'May 5th 2024, 5:53:55 am'
    date_str = date_str.split(',')[0] + date_str.split(',')[1]  # Remove the "th", if present
    date_str = date_str.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')
    date_obj = datetime.datetime.strptime(date_str, "%B %d %Y %I:%M:%S %p")
    return date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('zerotolerance-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    name = card.find('h5').text.strip() if card.find('h5') else "No Title"
                    date_text = card.find('p', {'class': 'text-center card-text'}).text.strip() if card.find('p', {'class': 'text-center card-text'}) else "No Date"
                    date = parse_and_format_date(date_text) if date_text != "No Date" else "No Date"
                    link = card.parent['href'].strip() if card.parent.name == 'a' else ""
                    link = find_slug_by_md5('zerotolerance', extract_md5_from_filename(html_doc)) + str(link)
                    description = " ".join([p.text.strip() for p in card.find_all('p', {'class': 'card-text'})])
                    #description = re.sub(r'https://gofile.io/d/\S+', 'https://gofile.io/d/[REDACTED]', description)
                    description = description.replace('\n',' ')
                    appender(name,'zerotolerance',description,'',date,link)
                file.close()
        except:
            errlog('Zero Tolerance: ' + 'parsing fail')
            pass    
