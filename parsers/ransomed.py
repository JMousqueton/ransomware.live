
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |                  |    X     |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomed-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                card_elements = soup.find_all('div', class_='card')
                for card in card_elements:
                    victim_element = card.find('b', recursive=False)
                    if victim_element:
                        victim = victim_element.get_text(strip=True)
                        if victim in ['FAQ', 'Contact Us']:
                            continue
                        ul_element = card.find('ul', recursive=False)
                        if ul_element:
                            description = ' '.join([li.get_text(strip=True) for li in ul_element.find_all('li')])
                        else:
                            description = ''
                        appender(victim, 'ransomed',description,'','','')
                file.close()
        except:
            errlog('ransomed: ' + 'parsing fail')
            pass    
