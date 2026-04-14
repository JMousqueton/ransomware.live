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

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():

    # Define the date format to convert to
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    
    ## Get the ransomware group name from the script name 
    script_path = os.path.abspath(__file__)
    # If it's a symbolic link find the link source 
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py','')
    # else get the script name 
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py','')

    for filename in os.listdir(tmp_dir):
        #try:
            if filename.startswith(group_name+'-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                page_title = soup.title.string.strip() if soup.title else ""
                VALID_TITLES = {
                    "SKIRA TEAM - Hacking News Main Page",
                    "SKIRA TEAM",  
                }
                if page_title in VALID_TITLES:
                    for link in soup.find_all('a', href=True):
                        if '/news/' in link['href']:
                            text = link.text.strip()

                            if ":" in text:
                                _, rest = text.split(":", 1)
                                rest = rest.strip()
                            else:
                                rest = text

                            # --- 1) Extract date as raw string ---
                            published = ""
                            if ":" in text:
                                date_part, rest = text.split(":", 1)
                                published = date_part.strip()       # <-- RAW DATE KEPT AS STRING
                                rest = rest.strip()
                                try:
                                    dt = datetime.strptime(date_part.strip(), "%b, %d, %Y")
                                    final_dt = dt.replace(
                                        hour=0,
                                        minute=0,
                                        second=0,
                                        microsecond=0
                                    )
                                    published = final_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
                                except:
                                    published = ""
                                print('-->>>',published)
                            else:
                                rest = text


                            # --- 1) Remove size like "932.4 GiB is now leaked" or "7.4 TiB is now leaked" ---
                            # Pattern catches:
                            #   - "932.4 GiB is now leaked"
                            #   - "7.4 TiB leaked"
                            #   - etc.
                            rest = re.sub(r"\b\d+(?:\.\d+)?\s*(?:GiB|TiB)[^,]*$", "", rest, flags=re.IGNORECASE).strip()
                            rest = re.sub(r"\b\d+(?:\.\d+)?\s*(?:GiB|TiB)\s+is\s+now\s+leaked\b", "", rest, flags=re.IGNORECASE).strip()


                            # --- 2) Extract website ---
                            website = ""
                            if " - " in rest:
                                left, website = rest.rsplit(" - ", 1)
                                website = website.strip().rstrip(".")
                            else:
                                left = rest

                            # --- 3) Extract country ---
                            country = ""
                            m = re.search(r"\(([^()]+)\)\s*$", left)
                            if m:
                                country = m.group(1).strip()
                                post_title = left[:m.start()].rstrip(" .")
                            else:
                                post_title = left.strip()

                            #post_title = re.sub(r'\s*\([^)]*\)\s*\.?$', '',  post_title).rstrip()
                            post_title = re.sub(r'\s*\([^)]*\)', '', post_title).strip().rstrip('.')
                            # print('--->', post_title)
                            
                            post = link['href']
                            post_url = find_slug_by_md5(group_name, extract_md5_from_filename(Path(html_doc).name)).replace('/news.html','') + post
                          
                            appender(
                                victim=post_title,
                                group_name=group_name,
                                description='',
                                website='',  # Optional, leave empty or populate if relevant data exists
                                published='',
                                post_url=post_url,
                                country=''  # Optional, leave empty or populate if relevant data exists
                            )
                            
                    file.close()
        #except Exception as e:
        #    errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)