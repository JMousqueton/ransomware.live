
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
from datetime import datetime
import re


def main():
    for filename in os.listdir('source'):
        #try:
            if filename.startswith('mogilevich-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for h3 in soup.find_all("h3"):
                    a_tag = h3.find("a")
                    website = a_tag.get("href")
                    victim = a_tag.text
                    # Extracting the date directly following the link
                    date_str = h3.text.split("|")[-1].strip()
                    original_date_str = date_str.strip().split('\n')[0].strip()
                    original_date_format = '%m.%d.%y'
                    target_format = '%Y-%m-%d %H:%M:%S.%f'
                    original_date = datetime.strptime(original_date_str, original_date_format)
                    formatted_date = original_date.strftime(target_format)
                    lines = date_str.strip().split('\n')
                    description =  '\n'.join(lines[1:]).replace('\n', ' ')
                    description = re.sub(r'\s+', ' ',description) 
                    appender(victim, 'mogilevich', description,website,formatted_date,'')
                    file.close()
        #except:
        #    errlog("Failed during : " + filename)
