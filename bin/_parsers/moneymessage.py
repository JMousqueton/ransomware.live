"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    for filename in os.listdir(tmp_dir):
        try:
           if filename.startswith('moneymessage-'):
                html_doc= tmp_dir / filename
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



