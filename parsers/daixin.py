import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('daixin-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "border border-warning card-body shadow-lg"})
                for div in divs_name:
                    title = div.find('h4').text.strip()
                    website = div.find('h6').text.strip().replace("Web Site:", "")
                    description = div.find('p').text.strip()
                    appender(title, 'daixin', description, website)
                file.close()
        except:
            errlog("Failed during : " + filename)