"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |          X       |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
import json
import html
import re
from sharedutils import errlog
from parse import appender 
from datetime import datetime
from urllib.parse import unquote


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('nokoyawa-'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart = soup.pre.contents
                data = json.loads(jsonpart[0])
                for entry in data['payload']:
                    title = html.unescape(entry['title'])
                    title = decoded_url = unquote(title)
                    website = str(entry['url'])
                    website = decoded_url = unquote(website)
                    url="nokoleakb76znymx443veg4n6fytx6spck6pc7nkr4dvfuygpub6jsid"
                    post_url = 'http://' + url + '.onion/leak/' +  entry['_id'].strip() 
                    description = html.unescape((re.sub(r'<[^>]*>', '',entry['description'])))
                    date_str = entry['createdAt']
                    dt_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    # datetime.datetime.strptime(date_str, "%Y-%B-%d").replace(hour=1, minute=2, second=3, microsecond=456789)
                    #published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title, 'nokoyawa', description.replace('\n',''),website,published,post_url)
                file.close()
        except:
            errlog('nokoyawa: ' + 'parsing fail')
            pass    
