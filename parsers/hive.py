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
        try:
            if filename.startswith('hive-hiveapi'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                htmlfile = file.read()
                jsonfile = re.sub(r'<[^>]+>', '', htmlfile)
                data = json.loads(jsonfile)
                for element in data:
                    title = element['title']
                    website = element['website']
                    try:
                        description = element['description'].replace('\n',' ')
                    except:
                        pass
                    appender(title, 'hive', description, website)
                file.close()
        except:
            errlog('hive: ' + 'parsing fail')
            pass    