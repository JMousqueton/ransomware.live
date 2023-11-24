
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |                | include in desc  |     x    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os
from bs4 import BeautifulSoup
from sharedutils import stdlog, errlog
from parse import appender


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('losttrust-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                
                # Find all div elements with class "card" (assuming there may be more companies)
                companies = soup.find_all('div', class_='card')

                # Iterate through each company
                for company in companies:
                    try: 
                        victim = company.find('div', class_='card-header').text.strip()
                    except: 
                        continue
                    description = company.find('div', class_='card-body').p.text.strip()
                    website = company.find('a', href=True, text='Visit site')['href']
                    appender(victim, 'losttrust', description.replace('\n',' '),"https://"+website)
                file.close()
        except:
            errlog('losttrust: ' + 'parsing fail')
            pass    
