import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender 

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('projectrelic-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "content"})
                for div in divs_name:
                    title = div.find('div', {'class': 'name'}).text.strip()
                    description =  div.find('div', {'class': 'description'}).text.strip()
                    # stdlog(title)
                    appender(title, 'projectrelic', description)
                file.close()
        except:
            errlog('projectrelic: ' + 'parsing fail')
            pass 
