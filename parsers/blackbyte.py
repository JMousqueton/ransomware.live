"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |          X       |          |
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
            if filename.startswith('blackbyte-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('table', {"class": "table table-bordered table-content"})
                # <table class="table table-bordered table-content ">
                for div in divs_name:
                    title = div.find('h1').text.strip()
                    description = div.find('p').text.strip().replace("\n", "")
                    website = div.find('a')
                    website = website.attrs['href']
                    appender(title, 'blackbyte', description,website)
                file.close()
        except:
            errlog('blackbyte: ' + 'parsing fail')
            pass