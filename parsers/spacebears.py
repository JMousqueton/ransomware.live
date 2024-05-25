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
from datetime import datetime, timedelta


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('spacebears-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                company_blocks = soup.find_all('div', class_='companies-list__item')
                for block in company_blocks:
                    image_block = block.find('div', class_='image-block')
                    name_tag = block.find('div', class_='name').find('a')
                    victim = name_tag.text.strip()
                    post_url = name_tag['href']
                    description_tag = block.find('div', class_='text') #.find('p')
                    description = description_tag.text.strip() if description_tag else 'No description available'
                    description = description.replace('\n',' ')
                    if image_block:
                        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        published_tag = image_block.find('p')
                        if published_tag and 'Published' in published_tag.text:
                            # Extract the number of days and calculate the publication date
                            days_ago_text = published_tag.text.strip()
                            days_ago = int(days_ago_text.split()[1])
                            publication_date = current_date - timedelta(days=days_ago)
                            date = publication_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                        else:
                            date = ''
                    words = description.split() 
                    website = words[-1]
                    appender(victim,'spacebears',description,website,date,post_url)
                file.close()
        except:
            errlog('SpaceBears: ' + 'parsing fail')
