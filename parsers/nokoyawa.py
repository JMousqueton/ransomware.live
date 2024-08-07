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
from urllib.parse import unquote


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('nokoyawa-'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                #stdlog('-->' + html_doc)
                soup=BeautifulSoup(file,'html.parser')
                try:
                    jsonpart = soup.pre.contents
                    data = json.loads(jsonpart[0])
                    for entry in data['payload']:
                        title = html.unescape(entry['title'])
                        title = decoded_url = unquote(title)
                        website = str(entry['url'])
                        website = decoded_url = unquote(website)
                        #url = find_slug_by_md5('nokoyawa', extract_md5_from_filename(html_doc))
                        url="http://nokoleakb76znymx443veg4n6fytx6spck6pc7nkr4dvfuygpub6jsid.onion"
                        post_url =  url + '/leak/' +  entry['_id'].strip() 
                        description = html.unescape((re.sub(r'<[^>]*>', '',entry['description'])))
                        date_str = entry['createdAt']
                        dt_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        # datetime.datetime.strptime(date_str, "%Y-%B-%d").replace(hour=1, minute=2, second=3, microsecond=456789)
                        #published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                        published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                        appender(title, 'nokoyawa', description.replace('\n',' '),website,published,post_url)
                    file.close()
                except:
                    stdlog('nokoyawa: '+ html_doc + ' is not a json file - parsing fail')
        except:
            errlog('nokoyawa: ' + 'parsing fail')
            pass    
