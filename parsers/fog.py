
"""
    From Template v3 - 20240807
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |     X     |     X    |
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
    for filename in os.listdir('source'):
        try:
            if filename.startswith(group_name+'-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                post_divs = soup.find_all('div', class_='h-full rounded-2xl bg-stone-200/50 from-orange-900 via-amber-700 to-white p-[1px] text-sm shadow-[inset_0_0_0_1px_rgba(255,255,255,0.4)] hover:bg-gradient-to-r dark:bg-gray-900')
                for post_div in post_divs:
                    date_str = post_div.find('div', class_='flex justify-between pb-4 text-xs').p.string
                    date_obj = datetime.strptime(date_str, '%a, %B %d, %Y')
                    published = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    title = post_div.find('p', class_='pb-4 text-lg font-bold').string
                    description = post_div.find('p', class_='line-clamp-6 pt-4').string
                    link = post_div.find_parent('a')['href']
                    url = find_slug_by_md5(group_name, extract_md5_from_filename(html_doc))
                    url = url + link.replace('/posts/posts/','/posts/')
                    if title != "00":
                        appender(title.replace('|','-'), group_name, description, '',published,url )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)