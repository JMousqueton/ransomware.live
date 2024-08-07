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
                soup=BeautifulSoup(file,'html.parser')
                ##divs_name = soup.find_all('div', {"class": "col-lg-4 col-sm-6 mb-4"})
                for div in soup.find_all("div", class_="block relative p-8 bg-gray-800 rounded-lg transition duration-300 ease-in-out"):
                    company_name = div.find("h2", class_="font-bold text-yellow-500 mb-4 break-words uppercase").text.strip()
                    company_website = div.find("a", class_="text-blue-400 text-sm ml-1 hover:text-blue-300")["href"]
                    spans = div.find_all("span", class_="text-white text-sm ml-1")
                    published_date_text = spans[1].text.strip() if len(spans) > 1 else None
                    published_date = datetime.strptime(published_date_text, "%B %d, %Y").strftime("%Y-%m-%d %H:%M:%S.%f") if published_date_text else None
                    description = div.find("p", class_="p-2 mt-1 text-gray-400 text-mg mb-6 overflow-y-auto whitespace-pre-wrap border border-gray-700 rounded-lg").text.strip()
                    link_to_post = div.find("a", class_="inline-flex items-center justify-center bg-gray-900 text-white py-2 px-4 border border-gray-600 hover:border-gray-400 rounded shadow hover:shadow-md transform hover:scale-105 transition ease-in-out duration-300 text-sm font-medium absolute bottom-0 right-0 mb-3 mr-6")["href"]
                    link_to_post =  find_slug_by_md5(group_name, extract_md5_from_filename(html_doc))  + link_to_post
                    appender(company_name, group_name, description.replace('\n',' '),company_website,published_date,link_to_post )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)