
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |      X         |                 |     x    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import os, re
from datetime import datetime
#from bs4 import BeautifulSoup
import re
from sharedutils import stdlog, errlog
from parse import appender


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('toufan-'):
                html_doc='source/'+filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                
                pattern = r'<a\s+href="(http://[^"]+)".*?>(.*?)</a>'
                matches = re.findall(pattern, html_content)
                for match in matches:
                    website = match[0]
                    victim = remove_html_tags(match[1])
                    #print(f"Website: {website}")
                    #print(f"Victim: {victim}\n")                        
                    appender(victim, 'toufan', '',website,'','','IL')
                file.close()
        except:
           errlog('toufan : ' + 'parsing fail')
           pass    
