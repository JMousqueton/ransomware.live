"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                |        X         |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename,stdlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        #try:
           if filename.startswith('knight-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card-body p-3 pt-2"})
                for div in divs_name:
                    tmp = div.find('a',{"class":"h5"})
                    title = tmp.text 
                    post = tmp.get('href')
                    url = find_slug_by_md5('knight', extract_md5_from_filename(html_doc))
                    url =  url + post
                    description = div.find("p").text.strip()
                    appender(title, 'knight',description.replace('\n',' '),'','',url)
                divs_name=soup.find_all('div', {"class": "card-body"})
                for div in divs_name:
                    try:
                        h2 = div.find('h2',{"class":"card-title"})
                        title = h2.text.strip()
                        description = div.find("p").text.strip()
                        post = h2.a['href']
                        url = find_slug_by_md5('knight', extract_md5_from_filename(html_doc))
                        url =  url + post
                        appender(title, 'knight', description.replace('\n',''),'','',url)
                    except:
                        pass
                file.close()
        #except:
        #    errlog('knight: ' + 'parsing fail')
        #    pass
