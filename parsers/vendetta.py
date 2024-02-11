import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('vendetta-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {'class':'post'})
                for div in divs_name:
                    title = div.a['href'].split('/')[2]
                    description = div.find('p', {'class': 'text'}).text.strip()
                    appender(title, 'vendetta', description)
                file.close()
        except:
            errlog('vendetta: ' + 'parsing fail')
            pass
