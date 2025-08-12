"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('killsec-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('a', {"class": "post-block unleaked"})
                address  = find_slug_by_md5('killsec', extract_md5_from_filename(str(html_doc))) 
                for div in divs_name:
                    title = div.find('div',{"class": "post-title"}).text.strip()
                    description = div.find('p',{"class" : "post-block-text"}).text.strip()
                    try :
                        link =  address + '/' + div['href']
                    except:
                        link = ''
                    appender(title,'killsec',description,'','',link)
                divs_name=soup.find_all('a', {"class": "post-block leaked"})
                for div in divs_name:
                    title = div.find('div',{"class": "post-title"}).text.strip()
                    description = div.find('p',{"class" : "post-block-text"}).text.strip()
                    try :
                        link =  address + '/' + div['href']
                    except:
                        link = ''
                    appender(title,'killsec',description,'','',link)

                ## killsec 3


                
                # Extract data from <a> tags
                
                bp = soup.find('bp')
                if bp:
                    side = bp.find('side')
                    if side:
                        ls = side.find('ls')
                        if ls:
                            for a in ls.find_all('a'):
                                href =  a['href']
                                id = a['id']
                                stat = a['stat']
                                title_line = a['title']
                                # disclosure_count = a.find('cont').text
                                value = a.find('r').text.strip() if a.find('r') else None
                                if '$' not in value:
                                    value = 'N/A'
                                country_img = a.find('img')['src'] if a.find('img') else None
                                titles = [part.strip() for part in title_line.split('-')]
                                appender(titles[0],'killsec',value, titles[1],'',address + '/posts.php' + href)
                                
        except Exception as e:
            errlog('killsec - parsing fail with error: ' + str(e) + 'in file:' + filename)


            