"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |         |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
#import re
#import json
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('moneymessage-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                """
                htmlfile = file.read()
                jsonfile = re.sub(r'<[^>]+>', '', htmlfile)
                data = json.loads(jsonfile)
                title = data['name'].strip()
                #published = data['incidentDate']
                #date_obj = datetime.strptime(published, "%d.%m.%Y")
                #published = datetime.strftime(date_obj, "%Y-%m-%d %H:%M:%S.%f")
                description = data["description"].replace('\n', '').replace('\r', '')
                """
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "MuiBox-root css-0"})
                for div in divs_name:
                    title = div.find('h5').text
                    description = div.find("div", {"class": "css-1j63rwj"}).text.strip()
                    appender(title, 'moneymessage', description)
                file.close()
        except:
            errlog('moneymessage: ' + 'parsing fail')
            pass

