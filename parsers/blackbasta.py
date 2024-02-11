
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                | include in desc  |     x    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import stdlog, errlog
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('blackbasta-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('a', {"class": "blog_name_link"})
                    post = title.get('href').replace("https","http").replace(" ","%20")
                    title = title.text.strip()
                    descs = div.find_all('p')
                    description = ''
                    for desc in descs:
                        description += desc.text.strip()
                    appender(title, 'blackbasta', description.replace('\n',' ').replace('ADDRESS',' Address '),"","",post)
                file.close()
        except:
            errlog('blackbasta: ' + 'parsing fail')
            pass    
