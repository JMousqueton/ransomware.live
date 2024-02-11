"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |       X        |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
import re
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
import json
from datetime import datetime


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomhouse-'):
                date_format = "%d/%m/%Y"
                desired_format = "%Y-%m-%d %H:%M:%S.%f"
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart= soup.pre.contents 
                data = json.loads(jsonpart[0]) 
                for element in data['data']:
                    title = element['header']
                    link = element['id']
                    url = 'zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid'
                    post_url = 'http://' + url + '.onion/r/' + link
                    website = element['url']
                    try:
                        date_string = element['actionDate']
                        datetime_obj = datetime.strptime(date_string, date_format)
                        formated_date = datetime_obj.strftime(desired_format)
                    except:
                        formated_date = ''
                    description = re.sub(r'<[^>]*>', '',element['info'])
                    appender(title, 'ransomhouse', description,website,formated_date,post_url)
                file.close()
        except:
            errlog('ransomhouse: ' + 'parsing fail')
            pass