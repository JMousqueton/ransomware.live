"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
Codé par @JMousqueton pour Ransomware.live
"""

import os
from bs4 import BeautifulSoup
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('meow-'):
                html_doc='source/'+filename
                #stdlog('processing ' + filename)
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                story_cards = soup.find_all('div', class_='MuiCard-root')
                for card in story_cards:
                    # Extract information from each card
                    url_site = find_slug_by_md5('meow', extract_md5_from_filename(html_doc))
                    card_link = card.find('a')['href']
                    card_link = url_site + card_link
                    title = card.find('div', class_='MuiTypography-h5').text.strip()
                    
                    # Convert date to desired format
                    raw_date = card.find('p', class_='story-createdAt').text.strip()
                    date_object = datetime.strptime(raw_date, '%d %B ,%Y')
                    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S.%f')


                    #image_url = card.find('div', class_='MuiCardMedia-root')['style'].split('url("')[1].split('")')[0]
                    leak_status = card.find('div', class_='MuiAlert-message').text.strip()

                    appender(title, "meow", leak_status, "", formatted_date, card_link)
                file.close()
        except:
            errlog('meow: ' + 'parsing fail')
            pass    
