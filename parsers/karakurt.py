import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender 

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('karakurt-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('article', {"class": "ciz-post"})
                for div in divs_name:
                    title = div.h3.a.text.strip()
                    try:
                        description = div.find('div', {'class': 'post-des'}).p.text.strip()
                    except:
                        pass 
                        #errlog('karakurt: ' + 'parsing fail')
                    appender(title, 'karakurt', description.replace('\nexpand',''))
                divs_name=soup.find_all('div', {"class": "category-mid-post-two"})
                for div in divs_name:
                    title = div.h2.a.text.strip()
                    try:
                        description = div.find('div', {'class': 'post-des dropcap'}).p.text.strip()
                    except:
                        pass
                    #    errlog('karakurt: ' + 'parsing fail')
                    appender(title, 'karakurt', description.replace('\nexpand',''))
                file.close()
        except:
            errlog('karakurt: ' + 'parsing fail')
            pass 