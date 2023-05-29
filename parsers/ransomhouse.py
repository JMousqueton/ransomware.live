"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
import re
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
import json

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomhouse-zoh'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart= soup.pre.contents # type: ignore
                data = json.loads(jsonpart[0]) # type: ignore
                for element in data['data']:
                    title = element['header']
                    link = element['id']
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    post_url = 'http://' + url + '.onion/r/' + link
                    website = element['url']
                    description = re.sub(r'<[^>]*>', '',element['info'])
                    # stdlog(title)
                    appender(title, 'ransomhouse', description,website,'',post_url)
                file.close()
        except:
            errlog('ransomhouse: ' + 'parsing fail')
            pass