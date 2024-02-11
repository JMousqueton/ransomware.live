import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('avoslocker-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('h5', {"class": "card-brand"}).text.strip()
                    description = div.find('div', {"class": "card-desc"}).text.strip()
                    appender(title, 'avoslocker',description.replace('\n',' '))
                file.close()
        except:
            errlog('avoslocker: ' + 'parsing fail')
            pass