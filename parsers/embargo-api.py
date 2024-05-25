
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |         X      |                  |     X    |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os
import json
from sharedutils import errlog, stdlog
from parse import appender
from datetime import datetime
import requests
from parse import appender
import urllib3

# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}
def get_fqdns_from_json(filename, group_name):
    with open(filename, 'r') as file:
        data = json.load(file)
    fqdns = []
    for item in data:
        if item.get("name") == group_name:
            for location in item.get("locations", []):
                fqdns.append(location["fqdn"])
            break

    return fqdns

def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies,verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    return json_data

def convert_datetime(iso_datetime):
    dt_obj = datetime.fromisoformat(iso_datetime)
    formatted_datetime = dt_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime

def main():
    filename = "groups.json"
    group_name = "embargo"
    fqdns = get_fqdns_from_json(filename, group_name)   
    for fqdn in fqdns:
        #onion_url= 'http://embargobe3n5okxyzqphpmk3moinoap2snz5k6765mvtkk7hhi544jid.onion/api/blog/get'
        onion_url = 'http://' + fqdn + '/api/blog/get'
        stdlog('Fetching :'+onion_url) 
        json_data = fetch_json_from_onion_url(onion_url)
        stdlog(onion_url+" Fetched")
        if json_data is not None:
            for item in json_data:
                id = item['_id']
                title = item['comname'].strip()
                description = item['descr']
                comments = item['comments']
                date_created = item['date_created']
                pubdate = convert_datetime(date_created)
                post_url= 'http://' + fqdn + '/#/post/'
                post_url = post_url + str(id) 
                appender(title,'embargo',description + ' - ' +  comments,'',pubdate,post_url)
