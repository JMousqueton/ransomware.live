"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('akira-'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart = soup.pre.contents
                data = json.loads(jsonpart[0])
                for entry in data:
                    title = html.unescape(entry['title'])
                    date_str = entry['date']
                    description = entry['content']
                    #dt_object = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=1, minute=2, second=3, microsecond=456789)
                    dt_object = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    # Get the current time
                    current_time = datetime.datetime.now().time()
                    # Combine the parsed date with the current time
                    combined_datetime = datetime.datetime.combine(dt_object.date(), current_time)
                    published = combined_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
                    #published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title.replace('\n',''), 'akira', description.replace('\n',' '),'',published)
                file.close()
        except:
            errlog('akira: ' + 'parsing fail')
            pass    
