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
import urllib3
import socks
import requests
## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def fetch_json(url):
    try:
        response = requests.get(url, proxies=proxies,verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def extract_and_convert_data(json_data):
    items = json_data["data"]["items"]
    for item in items: 
        try:
            company_name = item["company_name"]
            company_name = company_name.replace('Part1','').replace('PART2','').replace(' - ','').replace('https://','').replace('http://','')
            id =  item["id"]
            uploaded_date =  convert_date_format(item["uploaded_date"])
            description =  item["brief_description"]
            url="http://e27z5kd2rjsern2gpgukhcioysqlfquxgf7rxpvcwepxl4lfc736piyd.onion/blogs/"+str(id)
            """
            +------------------------------+------------------+----------
            | Description | Published Date | Victim's Website | Post URL |
            +------------------------------+------------------+----------+
            |      X      |      X         |                 |     x    |
            +------------------------------+------------------+----------+
            Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
            """
            appender(company_name.strip(),'dispossessor',description,'',uploaded_date,url)
        except:
            pass

def convert_date_format(date_string):
    dt = datetime.strptime(date_string, "%d %b, %Y %H:%M:%S UTC")
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

def main():
    # base_url = "https://dispossessor.com/back/getallblogs?search=&page={}"
    base_url = "http://e27z5kd2rjsern2gpgukhcioysqlfquxgf7rxpvcwepxl4lfc736piyd.onion/back/getallblogs?search=&page={}"
    page = 1
    all_data = []

    # Fetch the first page to get the total number of pages
    json_response = fetch_json(base_url.format(page))
    if json_response and json_response["success"]:
        total_pages = json_response["data"]["totalPages"]
        stdlog("    Parsing [1/"+ str(total_pages)+"]")
        extract_and_convert_data(json_response)

        # Fetch the rest of the pages
        for page in range(2, total_pages + 1):
            stdlog("    Parsing [" +  str(page) + "/"+ str(total_pages)+"]")
            json_response = fetch_json(base_url.format(page))
            if json_response and json_response["success"]:
                extract_and_convert_data(json_response)
            else:
                stdlog("Failed to fetch page " + page)


if __name__ == "__main__":
    main()