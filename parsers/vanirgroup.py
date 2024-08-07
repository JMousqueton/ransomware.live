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
import json

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender

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

    for filename in os.listdir('source'):
        try:
            if filename.startswith(group_name+'-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                content = file.read()
                matches = re.search('projects:(.*)}}},P', content, re.IGNORECASE)
                myjson= matches.group(1).replace("projectName:", '"projectName":')\
                         .replace("projectDescription:", '"projectDescription":')\
                         .replace("githubLink:", '"githubLink":')\
                         .replace("websiteLink:", '"websiteLink":')\
                         .replace("tags:", '"tags":')
                data = json.loads(myjson) # type: ignore
                for entry in data:
                    title = entry['projectName'].strip()
                    description = entry['projectDescription'].strip()
                    appender(title, group_name, description )
        except Exception as e:
            stdlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)