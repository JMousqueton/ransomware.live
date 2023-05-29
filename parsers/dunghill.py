
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
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('dunghill_leak-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                title = soup.find('div', {"class": "block-heading pt-4 mt-5"}).text.strip() # type: ignore
                date_string = soup.find("div", {"class": "block__details-count cur_date_block"}).text.strip() # type: ignore
                date_object = datetime.strptime(date_string.replace('p.m.','pm'), "%B %d, %Y, %I:%M %p")
                output_format = "%Y-%m-%d %H:%M:%S.%f"
                date = date_object.strftime(output_format)
                description = soup.find("div", {"class": ""}).text.strip() # type: ignore
                appender(title, 'dunghill_leak', description,'',str(date))
                file.close()
        except:
            errlog('dunghill_leak: ' + 'parsing fail')
            pass    
