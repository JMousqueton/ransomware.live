""" 
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |         X        |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""
import requests
import socks
import json
from sharedutils import stdlog, dbglog, errlog   # , honk
from sharedutils import openjson
from datetime import datetime
from parse import appender
import re


# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies,verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        stdlog("Error:", e)
        return None
    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    return json_data

def remove_html_tags(text):
    # Regular expression for matching HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_date_or_current(date_str):
    try:
        # Parse the original date format
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        # Return the current date-time if the original format is invalid
        date_obj = datetime.now()
    
    # Reformat to the desired format
    return date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")


def main():
    url= 'http://krsbhaxbki6jr4zvwblvkaqzjkircj7cxf46qt3na5o5sj2hpikbupqd.onion/api'
    data = fetch_json_from_onion_url(url)
    if data is not None:
        # Extracting the 'data' field
        leaks_data = data.get('data', {}).get('leaks', [])

        # Iterating through the leaks and printing details
        for leak in leaks_data:
            title = leak.get('title')
            description = remove_html_tags(leak.get('short_descryption', ''))
            website = leak.get('external_link','')
            pubdate = convert_date_or_current(leak.get('created_at'))
            link = url.replace('api','') + 'leak/' +  str(leak['rndid'])
            appender(title, 'trigona', description.replace('\n',' '),website, pubdate, link)
