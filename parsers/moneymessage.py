"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

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



