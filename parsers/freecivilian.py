import os
from bs4 import BeautifulSoup
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('freecivilian-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('section', {"id": "openSource"})
                for div in divs_name:
                    for item in div.find_all('a',{'class':"a_href"}) :
                        # (item.text.replace(' - ','#').split('#')[0].replace('+','').strip())
                        appender(item.text.replace(' - ','#').split('#')[0].replace('+','').strip(),'freecivilian')
            file.close()                
        except:
            # errlog('freecivilian: ' + 'parsing fail')
            pass
