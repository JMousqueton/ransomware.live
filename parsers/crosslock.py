"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |          X       |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('crosslock-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "blog-posts"})
                for div in divs_name:
                    title = div.find('h2').text.strip()
                    descriptions = div.find_all('p')
                    description=''
                    for p in descriptions:
                        description +=p.text.strip()
                    appender(title, 'crosslock', description)
                file.close()
        except:
            errlog('crosslock: ' + 'parsing fail')
            pass

