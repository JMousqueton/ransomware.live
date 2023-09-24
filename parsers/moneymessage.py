"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |         |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
#import re
#import json
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender
from datetime import datetime

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('moneymessage-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup = BeautifulSoup(file, "html.parser")

                # Find all <a> elements with the specified class
                a_elements = soup.find_all("a", class_="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone css-j1mjqc")

                # Extract the link, title, and date information and store them in lists
                links = [a["href"] for a in a_elements]
                titles = [a.find("p").get_text() for a in a_elements]

                # Print the extracted information
                for link, title in zip(links, titles):
                    link = "http://blogvl7tjyjvsfthobttze52w36wwiz34hrfcmorgvdzb6hikucb7aqd.onion"+link
                    linn = ""
                    appender(title, 'moneymessage', '','','',link)

                a_elements = soup.find_all("a", class_="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone css-xvpw3o")

                # Extract the link, title, and date information and store them in lists
                links = [a["href"] for a in a_elements]
                titles = [a.find("p").get_text() for a in a_elements]

                # Print the extracted information
                for link, title in zip(links, titles):
                    link = "http://blogvl7tjyjvsfthobttze52w36wwiz34hrfcmorgvdzb6hikucb7aqd.onion"+link
                    link = ""
                    appender(title, 'moneymessage', '','','',link)
                file.close()
        except:
            errlog('moneymessage: ' + 'parsing fail')
            pass



