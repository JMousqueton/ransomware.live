
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
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        #try:
            if filename.startswith('stormous-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, 'html.parser')
                items = soup.find_all('div', class_='item')
                for item in items:
                    title = item.find('h3').text.strip()
                    description = item.find('p').text.strip()
                    # link = 'http://h3reihqb2y7woqdary2g3bmk3apgtxuyhx4j2ftovbhe3l5svev7bdyd.onion/' + item.find('a', href=re.compile('.html')).get('href')
                    link = ''
                    button_tag = item.find('button', text='DETAILS')
                    if button_tag:
                        parent_a_tag = button_tag.find_parent('a')
                        if parent_a_tag and 'href' in parent_a_tag.attrs:
                            link =  'http://h3reihqb2y7woqdary2g3bmk3apgtxuyhx4j2ftovbhe3l5svev7bdyd.onion/' + parent_a_tag['href']

                    appender(title, 'stormous', description,'','',link)
                file.close()
        #except:
        #    errlog('stormous: ' + 'parsing fail')
        #    pass 