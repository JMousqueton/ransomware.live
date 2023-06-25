
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
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
        #try:
            if filename.startswith('lorenz-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                panels = soup.find_all('div', {'class': 'panel panel-primary'})
                for panel in panels:
                    panel_heading = panel.find('div', {'class': 'panel-heading'})
                    title = panel_heading.find('h3').text.strip()
                    posted_date_str = panel_heading.find('h5').text.strip().replace('Posted', '').replace('.', '').strip()
                    website_link = panel_heading.find('a', {'style': 'color: #ffffff'}).get('href')


                    try:
                        # Convert posted_date_str to a datetime object
                        posted_date = datetime.strptime(posted_date_str, '%b %d, %Y')

                        # Format the posted_date as desired (YYYY-MM-DD HH:MM:SS.000000)
                        formatted_date = posted_date.strftime('%Y-%m-%d %H:%M:%S.%f')

                    except ValueError:
                        print('Invalid date:', posted_date_str)
                        print('Using current date instead.')
                        posted_date = datetime.today()
                        formatted_date = datetime.combine(posted_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S.%f')


                    appender(title, 'lorenz','_URL_',website_link,formatted_date)

                
                file.close()
        #except:
        #    errlog('lorenz : ' + 'parsing fail')
        #    pass
