
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |          X       |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('dunghill_leak-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs = soup.find_all('div',{"class": "custom-container"})
                for div in divs:
                    title = div.find('div', {"class": "ibody_title"}).text.strip()
                    description = div.find("div", {"class": "ibody_body"}).find_all('p')
                    description = description[2].text.strip()
                    link = "http://p66slxmtum2ox4jpayco6ai3qfehd5urgrs4oximjzklxcol264driqd.onion/" + div.find('div', {"class": "ibody_ft_right"}).a['href']
                    appender(title, 'dunghill', description,'','',link)
                divs = soup.find_all('div',{"class": "custom-container2"})
                for div in divs:
                    title = div.find('div', {"class": "ibody_title"}).text.strip()
                    description = div.find("div", {"class": "ibody_body"}).find_all('p')
                    description = description[2].text.strip()
                    link = "http://p66slxmtum2ox4jpayco6ai3qfehd5urgrs4oximjzklxcol264driqd.onion/" + div.find('div', {"class": "ibody_ft_right"}).a['href']
                    appender(title, 'dunghill', description,'','',link)
                file.close()
        except:
            errlog('dunghill_leak: ' + 'parsing fail')
            pass    
