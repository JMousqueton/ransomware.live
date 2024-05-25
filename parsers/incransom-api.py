import requests
import socks
import json
from sharedutils import stdlog, dbglog, errlog   # , honk
from sharedutils import openjson
from datetime import datetime
from urllib.parse import unquote
from parse import appender

"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

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


def main():
    json_onion_url= 'http://incbackfgm7qa7sioq7r4tdunoaqsvzjg5i7w46bhqlfonwjgiemr7qd.onion/api/v1/blog/get/announcements'
    site_onion_url= 'http://incblog6qu4y4mm4zvw5nrmue6qbwtgjsxpw6b7ixzssu36tsajldoad.onion/blog/disclosures'
    try:
        json_data = fetch_json_from_onion_url(json_onion_url)
    except:
        json_data = None
    if json_data is not None:
        announcements = json_data['payload']['announcements']
        for announcement in announcements:
            company_id = announcement['_id']
            company_name = unquote(announcement['company']['company_name'])
            description = unquote(" ".join(announcement['description']))
            creation_date = datetime.fromtimestamp(announcement['createdAt'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
            post_url=site_onion_url+'/'+company_id
            appender(company_name,'incransom',description,'',creation_date,post_url)