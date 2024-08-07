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
from html import unescape
## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


def main():
    for filename in os.listdir('source'):
            if filename.startswith('malas-'):
                html_doc='source/'+filename
                with open(html_doc, "r") as file:
                    html = file.read()

                titles = re.findall(r'<title>(.*?)</title>', html, re.DOTALL)
                links = re.findall(r'<link>(.*?)</link>', html, re.DOTALL)
                descriptions = re.findall(r'<description>(.*?)</description>', html, re.DOTALL)
                publisheds = re.findall(r'<pubDate>(.*?)</pubDate>', html, re.DOTALL)

                for title,link, published, description in zip(titles, links,publisheds,descriptions):
                        parsed_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                        encoded_description = unescape(description)
                        clean_description = re.sub(r"<.*?>", "", encoded_description)
                        convert_description = clean_description.replace('&rsquo;','`')
                        appender(title,'malas',convert_description.replace('\n',' '),'',formatted_date,link)
