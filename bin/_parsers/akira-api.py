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
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, stdlog,errlog
from pathlib import Path
from dotenv import load_dotenv


from urllib.parse import unquote
import requests
import socks
import json
#import html
## Import Ransomware.live libs 

import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

# Headers for requests
headers = {}
    

def fetch_json_from_onion_url(onion_url, cookies):
    """
    Fetch JSON data from the given onion URL using the Tor proxy and provided cookies.
    """
    try:
        # Add all required headers
        headers.update({
            "Referer": "https://akiral2iz6a7qgd3ayp3l6yub7xx2uep76idk3u2kollpj5z3z636bad.onion/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Priority": "u=0",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "X-Requested-With": "XMLHttpRequest"
        })


        ## Log the request details
        #stdlog(f"Making request to: {onion_url}")
        #stdlog(f"Headers: {headers}")
        #stdlog(f"Cookies: {cookies}")

        # Send the GET request with cookies
        response = requests.get(onion_url, headers=headers, cookies=cookies, proxies=proxies, verify=False, timeout=(60, 60))
        response.raise_for_status()  # Check for any HTTP errors

        ## Log the raw response content
        #stdlog(f"Response status code: {response.status_code}")
        #stdlog(f"Response content: {response.text}")

        # Assuming the response contains JSON data
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        errlog(f"Error fetching JSON: {e}")
        return None

def get_csrf_token(onion_url):
    """
    Fetch the CSRF token and cookies from the onion site.
    """
    try:
        # Send a GET request to fetch the HTML content of the onion site
        response = requests.get(onion_url, proxies=proxies, verify=False, timeout=(60, 60))
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the HTML response with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the CSRF token in a <meta> tag
        csrf_element = soup.find('meta', {'name': 'csrf-token'})
        csrf_token = csrf_element['content'] if csrf_element and 'content' in csrf_element.attrs else None

        # Log and return cookies
        cookies = response.cookies
        app_session_cookie = cookies.get('_app_session')
        #stdlog(f"CSRF Token: {csrf_token}")
        #stdlog(f"_app_session Cookie: {app_session_cookie}")

        return csrf_token, cookies
    except requests.exceptions.RequestException as e:
        errlog(f"Error fetching CSRF token: {e}")
        return None, None
    except Exception as e:
        errlog(f"Unexpected error while parsing CSRF token: {e}")
        return None, None

def main():
    news_url = 'https://akiral2iz6a7qgd3ayp3l6yub7xx2uep76idk3u2kollpj5z3z636bad.onion/n'
    leak_url = 'https://akiral2iz6a7qgd3ayp3l6yub7xx2uep76idk3u2kollpj5z3z636bad.onion/l'
    site_onion_url= 'https://akiral2iz6a7qgd3ayp3l6yub7xx2uep76idk3u2kollpj5z3z636bad.onion/'

    # Fetch the CSRF token from the onion site
    csrf_token, cookies = get_csrf_token(site_onion_url)

    if csrf_token and cookies:
        headers["X-CSRF-Token"] = csrf_token
        #stdlog(f"CSRF Token obtained: {csrf_token}")

        # Use the cookies to fetch JSON data
        try:
            json_data = fetch_json_from_onion_url(news_url, cookies)
        except Exception as e:
            json_data = None
            errlog(f"No data in JSON: {e}")

        if json_data:
            for entry in json_data["objects"]:
                title = entry['title'].replace('\n','')
                description = entry['content']
                date = entry['date'] + " 00:00:00.000000"
                appender(title,"akira", description, '',date,'')
                
        else:
            errlog("Failed to fetch JSON data.")
        try:
            json_data = fetch_json_from_onion_url(leak_url, cookies)
        except Exception as e:
            json_data = None
            errlog(f"No data in JSON: {e}")

        if json_data:
            for entry in json_data["objects"]:
                title = entry['name'].replace('\n','')
                description = entry['desc']
                appender(title,"akira", description)
                
        else:
            errlog("Failed to fetch JSON data.")
    else:
        errlog("Failed to fetch CSRF token or cookies.")