"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('donutleaks-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                # divs_name=soup.find_all('div', {"class": "box post-box"})
                articles = soup.find_all("article")  

                # Regular expression pattern to extract the date in the desired format
                date_pattern = r"(\d{2}-\d{2}-\d{4})"

                # Extract article details
                for article in articles:
                    # Extract title
                    title = article.find("h2", class_="post-title").text.strip()

                    # Extract date and convert it to the desired format
                    date_string = article.find("time").get("datetime")
                    date = re.search(date_pattern, date_string).group(0)
                    date_formatted = date[6:10] + "-" + date[3:5] + "-" + date[0:2] + " 00:00:00.00000"

                    # Extract URL
                    url = article.find("a").get("href")

                    # Extract description
                    description = article.find("p", class_="post-excerpt").text.strip()

                    appender(title, 'donutleaks', description.replace('|','-'),'',date_formatted,'http://sbc2zv2qnz5vubwtx3aobfpkeao6l4igjegm3xx7tk5suqhjkp5jxtqd.onion'+url)
                file.close()
        except:
            errlog('donutleaks: ' + 'parsing fail')
            pass    
