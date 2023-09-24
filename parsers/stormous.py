
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

def main():
    for filename in os.listdir('source'):
        #try:
            if filename.startswith('stormous-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    # Find the image source and description
                    img_src = table.find('img')['src']
                    victim = img_src.replace('images/companyimage/','').replace('.jpg','').replace('.png','')
                    victim_name = victim.capitalize()
                    description = table.find('p', class_='description').text.strip()
                    url = find_slug_by_md5('stormous', extract_md5_from_filename(html_doc))
                    post_url = url.replace('stm.html','') + '/' + victim + '.html'
                    appender(victim_name,'stormous',description,'','',post_url)
                file.close()
        #except:
        #    errlog('stormous: ' + 'parsing fail')
        #    pass 