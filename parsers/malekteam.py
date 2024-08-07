"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from html import unescape
## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

# Function to clean text
def clean_text(text):
    # Replace multiple spaces, tabs, and newlines with a single space
    return re.sub(r'\s+', ' ', text)


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('malekteam-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for item in soup.find_all("div", class_="timeline_item"):
                    # Extract date text
                    date_text_div = item.find("div", class_="timeline_date-text")
                    if date_text_div:
                        # Remove span tags and their contents
                        for span in date_text_div.find_all("span"):
                            span.decompose()
                        date_text = date_text_div.get_text(strip=True)


                    # Extract description
                    description_div = item.find("div", class_="timeline_text")
                    description = clean_text(description_div.get_text(strip=True)) if description_div else ''

                    # Extract 'Read More' link
                    read_more_link = item.find("a", text="Read More")
                    if read_more_link and read_more_link.has_attr('href'):
                        post_url = read_more_link['href']
                        post_url = find_slug_by_md5('malekteam', extract_md5_from_filename(html_doc)) + post_url 
                    appender(date_text, 'malekteam', description,"","",post_url)
                file.close()
        except:
            errlog("Malekteam Failed during : " + filename)
