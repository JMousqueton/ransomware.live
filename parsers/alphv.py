"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |          X       |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
import json,re
from sharedutils import stdlog, errlog
import parse
import datetime

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('alphv-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                if 'alphvmmm' in filename:
                        stdlog('alphv : Parse ' +  'json file')
                        html_doc='source/'+filename
                        file=open(html_doc, 'r')
                        htmlfile = file.read()
                        jsonfile = re.sub(r'<[^>]+>', '', htmlfile)
                        data = json.loads(jsonfile)
                        for entry in data['items']:
                            title = entry['title'].strip()
                            parts = filename.split('-')
                            url = parts[1].replace('.html','')
                            post_url = 'http://' + url + '.onion/' +  entry['id'].strip() 
                            published = entry['createdDt']
                            timestamp = int(published) / 1000
                            dt_object = datetime.datetime.fromtimestamp(timestamp)
                            published = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")   
                            description =''
                            website =''
                            if 'publication' in entry and entry['publication'] is not None:
                                # Si oui, accédez au champ "description"
                                description = entry['publication']['description'].strip()
                                # description = entry['publication']['description'].strip()
                                website = entry['publication']['url'].strip()
                            parse.appender(title, 'alphv', description.replace('\n',' '), website, published,post_url)
                        file.close()
                else: 
                    stdlog('alphv : Parse ' +  'html file')
                    divs_name=soup.find_all('div', {'class': 'post-body'})
                    for div in divs_name:
                        title = div.find('div', {'class': 'post-header'}).text.strip()
                        description = div.find('div', {'class': 'post-description'}).text.strip()
                        parse.appender(title, 'alphv',description.replace('\n',' '))
                file.close()
        except:
            errlog('alphv: ' + 'parsing fail')
            pass