import os
from bs4 import BeautifulSoup
from parse import appender
from sharedutils import errlog

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('nokoyawa-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "relative bg-white rounded-lg shadow dark:bg-gray-700"})
                for div in divs_name:
                    title = div.find('h3').text.strip().split('\n')[0].strip()
                    description = div.find('p', {'class':"break-all"}).text.strip()
                    appender(title, 'nokoyawa',description.replace('\n',' '))
                file.close()
        except:
            errlog('nokoyawa: ' + 'parsing fail')
            pass