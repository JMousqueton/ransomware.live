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
import datetime

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


def anonymize_mega_urls_in_text(text):
    """
    Finds and anonymizes all MEGA.nz folder URLs in a given text string.

    Args:
    text (str): The text containing one or more MEGA.nz URLs.

    Returns:
    str: The text with anonymized MEGA.nz folder URLs.
    """
    # Regular expression pattern to match MEGA.nz folder URLs
    pattern = r"(https://mega\.nz/folder/[a-zA-Z0-9]+)(#\w+)"
    
    # Function to replace the folder identifier with asterisks
    def replace_with_asterisks(match):
        return match.group(1)[:24] + '*'*9 + match.group(2)
    
    # Replace all matches in the text
    anonymized_text = re.sub(pattern, replace_with_asterisks, text)
    return anonymized_text

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('qiulong-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for article in soup.find_all('article'):
                    title = article.find('h1', class_='entry-title')
                    published_date = article.find('time', class_='entry-date published')
                    if not published_date:
                        published_date = article.find('time', class_='entry-date published updated')
                    if title and published_date:
                        link = title.find('a')
                        date_str = published_date['datetime']
                        # Parse the datetime string to a datetime object
                        published_datetime = datetime.datetime.fromisoformat(date_str)
                        # Format the datetime with microseconds
                        pub_date = published_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
                        # Get all paragraphs in the article for description
                        paragraphs = article.find_all('p')
                        description = " ".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                        description = anonymize_mega_urls_in_text(description)
                        if link:
                            # Extract URL and text
                            post_url = link['href']
                        else:
                            post_url=''
                        victim = link.text.strip()
                        appender(victim,'qiulong',description,'',pub_date,post_url)
        except:
            errlog('Qiulong: ' + 'parsing fail')
            pass