"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,json, re
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
        try:
            if filename.startswith(group_name+'-'):
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                post_divs = soup.find_all('div', class_='h-full rounded-2xl bg-stone-200/50 from-orange-900 via-amber-700 to-white p-[1px] text-sm shadow-[inset_0_0_0_1px_rgba(255,255,255,0.4)] hover:bg-gradient-to-r dark:bg-gray-900')
                for post_div in post_divs:
                    date_str = post_div.find('div', class_='flex justify-between pb-4 text-xs').p.string
                    try:
                        date_obj = datetime.strptime(date_str, '%a, %B %d, %Y')
                        published = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    except:
                        published = ''
                    title = post_div.find('p', class_='pb-4 text-lg font-bold').string
                    description = post_div.find('p', class_='line-clamp-6 pt-4')
                    # Ensure description is not None before accessing `.string`
                    description = description.string.strip() if description and description.string else ""
                    link = post_div.find_parent('a')['href']
                    url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))
                    url = url + link.replace('/posts/posts/','/posts/')
                    if title != "00":
                        appender(title.replace('|','-'), group_name, description, '',published,url )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)