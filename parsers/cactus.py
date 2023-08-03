"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|       X     |      X         |                  |    X     |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
from bs4 import BeautifulSoup
from parse import appender
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('cactus-'):
                html_doc='source/'+filename
                file=open(html_doc,'r') 

                soup = BeautifulSoup(file, 'html.parser')

                # Extract article titles and content
                articles = soup.select('article')
                for article in articles:
                    date = article.select_one('span').text.strip()
                    url = "https://cactusbloguuodvqjmnzlwetjlpj6aggc6iocwhuupb47laukux7ckid.onion" + article.select_one('a').get('href')
                    input_date = datetime.strptime(date, "%B %d, %Y")
                    date = input_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                    title = article.select_one('h2').text.strip()
                    content = article.select_one('p').text.strip()
                    appender(title, 'cactus',content)
        except:
            errlog('blacksuit : ' + 'parsing fail')
            pass
