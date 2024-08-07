"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re,json
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('royal-royal4'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart = soup.pre.contents
                data = json.loads(jsonpart[0])
                for entry in data['data']:
                    title = html.unescape(entry['title'])
                    website = str(entry['url'])
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    post_url = 'http://' + url + '.onion/' +  entry['id'].strip() 
                    description = html.unescape((re.sub(r'<[^>]*>', '',entry['text'])))
                    date_str = entry['time']
                    dt_object = datetime.datetime.strptime(date_str, "%Y-%B-%d").replace(hour=1, minute=2, second=3, microsecond=456789)
                    published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title, 'royal', description.replace('\n',' '),website,published,post_url)
                file.close()
        except:
            errlog('royal: ' + 'parsing fail')
            pass    