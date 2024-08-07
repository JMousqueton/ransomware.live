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

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


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
