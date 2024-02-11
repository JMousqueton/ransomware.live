import os
from bs4 import BeautifulSoup
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('0mega-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('tr', {"class": "trow"})
                for div in divs_name:
                    item = div.find_all('td')
                    title = item[0].text.strip()
                    description = item[2].text.strip()
                    appender(title,'0mega',description)
            file.close()                
        except:
            # errlog('freecivilian: ' + 'parsing fail')
            pass