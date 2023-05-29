import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('cuba-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {'class':'list-text'})
                for div in divs_name:
                    title = div.a['href'].split('/')[2]
                    if '.onion' not in title: 
                        description = div.a.text.strip()
                        appender(title, 'cuba', description)
                file.close()
        except:
            errlog('cuba: ' + 'parsing fail')
            pass
