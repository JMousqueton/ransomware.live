import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('qilin-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "item_box"})
                for div in divs_name:
                    title = div.find('a',{"class": "item_box-title mb-2 mt-1"}).text.strip()
                    description = div.find('div',{"class": "item_box_text"}).text.strip()
                    website = div.find('a',{"class": "item_box-info__link"}).text.strip()
                    appender(title, 'qilin', description.replace('\n',' '), website)
                file.close()
        except:
            errlog('qilin: ' + 'parsing fail')
            pass    
