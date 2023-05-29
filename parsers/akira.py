"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
import json
import html
from sharedutils import errlog
from parse import appender 
import datetime

def main():
    for filename in os.listdir('source'):
        #try:
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
                    dt_object = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=1, minute=2, second=3, microsecond=456789)
                    published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title.replace('\n',''), 'akira', description.replace('\n',''),'',published)
                file.close()
        #except:
            #errlog('akira: ' + 'parsing fail')
            #pass    
