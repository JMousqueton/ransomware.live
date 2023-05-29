import os
import re
from bs4 import BeautifulSoup
import json
from sharedutils import errlog
from parse import appender

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