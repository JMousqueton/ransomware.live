"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="")
"""

import os,datetime,sys,json,re
from bs4 import BeautifulSoup
from datetime import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

def strip_html_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def cut_content_before_link(content):
        match = re.search(r"Download link", content)
        if match:
            return content[match.start():]
        return content

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('cactus-'):
                html_doc='source/'+filename
                file=open(html_doc,'r') 
                soup = BeautifulSoup(file, 'html.parser')

                # Find the script tag containing JSON data
                script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

                # Extract JSON content from the script tag
                json_content = script_tag.string

                # Parse the JSON data
                data = json.loads(json_content)

                # Access the required information
                posts_data = data['props']['pageProps']['posts']['data']

                # Print slug, title, content, and publishedAt for each post
                for post in posts_data:
                    title = post['attributes']['title'].replace('/','')
                    victim = title.split('\\')[0]
                    website = title.split('\\')[0].strip() if '\\' in title else title.strip()                  
                    published_at = datetime.strptime(post['attributes']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    postdate = published_at.strftime("%Y-%m-%d %H:%M:%S.%f")
                    #victim =  post['attributes']['slug']
                    content = strip_html_tags(post['attributes']['content'])
                    content = cut_content_before_link(content).replace('6wuivqgrv2g7brcwhjw5co3vligiqowpumzkcyebku7i2busrvlxnzid','***************')
                    post_url = post['attributes']['slug']  # Replace 'link_field' with actual field name
                    post_url = "https://cactusbloguuodvqjmnzlwetjlpj6aggc6iocwhuupb47laukux7ckid.onion/posts/" + post_url
                    appender(victim,'cactus',content,website,postdate,post_url)
        except Exception as e:
            errlog('cactus - parsing fail with error: ' + str(e) + 'in file:' + filename)