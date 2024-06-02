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
from sharedutils import errlog, find_slug_by_md5, extract_md5_from_filename
from parse import appender
from datetime import datetime


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('killsec-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                # Find all div elements with class "portfolio-content"
                post_blocks = soup.select('.post-block')
                # Iterate over each div and extract the link and href
                for post in post_blocks:
                    # Extract the title, which seems to be the victim's identifier
                    title = post.select_one('.post-title').text.strip() if post.select_one('.post-title') else 'No Title'
                    
                    # Extract the link associated with the post block, if available
                    link = post.get('href', '')
                    if link:
                        url = find_slug_by_md5('killsec', extract_md5_from_filename(html_doc)) + "/" + link
                    
                    # Extract the description from the post block's body
                    description = post.select_one('.post-block-text').text.strip() if post.select_one('.post-block-text') else 'No Description'
                    appender(title,'killsec',description.replace('\n',' '),'','',url)
                file.close()
        except:
            errlog('killsec: ' + 'parsing fail')
            pass
