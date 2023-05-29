"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|             |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
import json
import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ragnarlocker-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                script_tag = soup.find('script', text=lambda t: 'post_links' in t)
                post_links = None
                if script_tag:
                    # Recherche du texte qui suit la chaîne "var post_links ="
                    start_index = script_tag.text.find('var post_links =') + len('var post_links =')
                    # Recherche du texte qui suit le dernier point virgule de la variable
                    end_index = script_tag.text.find(';', start_index)
                    post_links = script_tag.text[start_index:end_index]
                data = json.loads(post_links)
                for element in data:
                    title = element['title']
                    parts = filename.split('-')
                    url = parts[1].replace('.html','')
                    link = 'http://' + url + '.onion/?' + element['link']
                    published = datetime.datetime.fromtimestamp(int(element['timestamp'])).strftime('%Y-%m-%d %H:%M:%S.%f')
                    appender(title, 'ragnarlocker',"", "", published,link)
                file.close()
        except:
            errlog('ragnarlocker: ' + 'parsing fail')
            pass
