"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('darkvault-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                post_blocks = soup.find_all("div", class_="post-block")
                for post_block in post_blocks:
                    # Extract the victim's name (post title)
                    post_title = post_block.find("div", class_="post-title").get_text(strip=True)  
                    
                    # Extract the description
                    description = post_block.find("div", class_="post-block-text").get_text(strip=True)
                    
                    # Extract the published date
                    # Extract the published date and convert it
                    published_text = post_block.find("div", class_="updated-post-date").get_text(strip=True).replace('Posted: ', '')
                    published_date = datetime.strptime(published_text, "%d %B, %Y")  # Parse the date
                    published = published_date.strftime("%Y-%m-%d 00:00:00.000000")  # Format the date
                    
                    # Extract the 'onclick' attribute to get the post URL part
                    onclick_attr = post_block.get("onclick")
                    post_url_part = onclick_attr.split("'")[1] if onclick_attr else ""
                    post_url = f"http://mdhby62yvvg6sd5jmx5gsyucs7ynb5j45lvvdh4dsymg43puitu7tfid.onion/{post_url_part}" if post_url_part else "URL not available"

                    # Print the extracted information
                    #print(f"Post Title: {post_title}")
                    #print(f"Description: {description}")
                    #print(f"Published: {published}")
                    #print(f"Post URL: {post_url}\n")
                    appender(post_title, 'darkvault', description, '', published, post_url)
                file.close()
        except:
            errlog('darkvault: ' + 'parsing fail')
            pass    


main()
