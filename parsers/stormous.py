
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os,re
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('stormous-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                target_div = soup.find("div", class_="h5 pd-20 mb-0", string="Last victims")
                data_table = target_div.find_next_sibling("table")
                rows = data_table.find_all('tr')[1:]
                for row in rows:
                    columns = row.find_all('td')
                    victim = columns[0].text.strip()
                    country=columns[1].text.strip()
                    size=columns[2].text.strip()
                    website=columns[3].text.strip()
                    date=columns[4].text.strip()
                    date=date_obj = datetime.strptime(date, "%d/%m/%Y")
                    published = date.strftime("%Y-%m-%d 00:00:00.000000")
                    appender(victim,'stormous',country,website,published,'')
                file.close()
        except:
            stdlog('stormous: ' + 'parsing fail')
            pass 
