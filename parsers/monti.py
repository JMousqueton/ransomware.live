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
import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        
        group_name = original_name.replace('.py','')
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py','')

    for filename in os.listdir('source'):
        try:
            if filename.startswith(group_name+'-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name = soup.find_all('div', {"class": "col-lg-4 col-sm-6 mb-4"})
                for div in divs_name:
                    title = div.find('h5').text.strip()
                    post = div.find('a')
                    post = post.get('href')
                    url = find_slug_by_md5('monti', extract_md5_from_filename(html_doc))
                    url =  url + post
                    description =  div.find('p').text.strip()
                    published = div.find('div', {'class': 'col-auto published'}).text.strip()
                    date_obj =  datetime.datetime.strptime(published, '%Y-%m-%d %H:%M:%S')
                    published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title, group_name, description,"",published,url )
        except Exception as e:
            errlog(f'{group_name}: parsing fail with error: {str(e)} on file {filename}')
                
