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

def remove_period_if_first_char(input_string):
    if input_string and input_string[0] == ".":
        return input_string[1:]
    else:
        return input_string

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ragroup-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "row"})
                for div in divs_name:
                    for item in div.find_all('a') :
                        title = item.text.strip()
                        url = item['href']
                        site = "pa32ymaeu62yo5th5mraikgw5fcvznnsiiwti42carjliarodltmqcqd"
                        post_url = 'http://' + site + '.onion' + remove_period_if_first_char(url)
                        title = title.replace('(Unpay-Full public)','')
                        title = title.replace('(Unpay)','')
                        title = title.replace('(Unpay-Partially public)','')
                        title = title.replace('(Unpay-Start Leaking)','')
                        title = title.replace('\t','')
                        if len(title) > 0: 
                            appender(title, 'ragroup', '','','',post_url)
                file.close()
        except:
            errlog('ragroup: ' + 'parsing fail')
            pass    
