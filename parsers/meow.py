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
            if filename.startswith('meow-'):
                html_doc='source/'+filename
                #stdlog('processing ' + filename)
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                cards = soup.find_all('div', class_='card')
                for card in cards:
                    title = card.find('h5').text 
                    #description = card.find('p').text if card.find('p') else ''
                    description = ''
                    if card.find('a'): 
                        link = card.find('a')['href'] 
                        #url = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc))
                        url = 'http://meow6xanhzfci2gbkn3lmbqq7xjjufskkdfocqdngt3ltvzgqpsg5mid.onion'
                        link = url + link
                    else:
                        link = ''
            
                    appender(title, "meow", description, "", "",link)
                file.close()
        except:
            errlog('meow: ' + 'parsing fail')
            pass    
