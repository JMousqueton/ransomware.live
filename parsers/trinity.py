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
                articles = soup.find_all('div', id=lambda x: x and x.startswith('article_'))
                for article in articles:
                    website = article.find_all('p')[0].text.split(':', 1)[1].strip()
                    description = article.find_all('p')[1].text.split(':', 1)[1].strip()
                    publication_time_str = article.find_all('p')[2].text.split(':', 1)[1].strip()
                    revenue = article.find_all('p')[3].text.split(':', 1)[1].strip()
                    link = article.find_next('a')['href']
                    victim = article.find_all('p')[4].text.split(':', 1)[1].strip()
                
                    publication_time = datetime.strptime(publication_time_str, '%Y-%m-%d %H:%M:%S %Z')    
                    publication = publication_time.strftime('%Y-%m-%d')
                    if link:
                        link = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc)) + link
                    if revenue:
                        description += " - Revenue: " +  revenue
                    if publication:
                        description += " - Publication date: " + publication

                    appender(victim, group_name, description,website,'',link)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file:' + filename)
