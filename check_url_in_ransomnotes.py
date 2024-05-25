#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Check for unknown .onion url in ransom notes for Ransomware.live 
By Julien Mousqueton 
'''
import os
import re
import json
import requests
from sharedutils import stdlog

# Paths
directory_to_search = './docs/ransomware_notes'
json_file_path = './groups.json'

# Add the exception URLs here
exception_urls = [
    'torpastezr7464pevuvdjisbvaf4yqi4n7sgz7lkwgqwxznwy5duj4ad.onion',
    'myosbja7hixkkjqihsjh6yvmqplz62gr3r4isctjjtu2vm5jg6hsv2ad.onion',
    'ragnarmj3hlykxstyanwtgf33eyacccleg45ctygkuw7dkgysict6xyd.onion',  # Seized by Police ;)
    'j3qxmk6g5sk3zw62i2yhjnwmhm55rfz47fdyfkhaithlpelfjdokdxad.onion',  # White page
    'monti5o7lvyrpyk26lqofnfvajtyqruwatlfaazgm3zskt3xiktudwid.onion'  # Page not Found
]


def find_onion_urls(directory):
    onion_urls = {}  # Changed to a dictionary
    onion_pattern = re.compile(r'https?://[a-z2-7]{56}\.onion\b|\b[a-z2-7]{56}\.onion\b')
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Split the file path and extract the last subdirectory name
            subdirectory_name = os.path.basename(os.path.dirname(file_path))
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = onion_pattern.findall(content)
                normalized_matches = [re.sub(r'^https?://', '', url) for url in matches]
                for url in normalized_matches:
                    if url in onion_urls:
                        onion_urls[url].append(subdirectory_name)  # Add the subdirectory name instead of the full path
                    else:
                        onion_urls[url] = [subdirectory_name]
    return onion_urls



def get_fqdn_from_json(json_file_path):
    fqdn_set = set()
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            locations = entry.get("locations", [])
            for location in locations:
                fqdn = location.get("fqdn", "")
                if fqdn:
                    fqdn_set.add(fqdn)
    return fqdn_set

def check_onion_urls_online(onion_urls_dict, exception_urls):
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050',
    }

    online_urls = {}
    for url, source_files in onion_urls_dict.items():
        if url in exception_urls:
            continue
        try:
            response = session.get(f'http://{url}', timeout=10)
            if response.status_code == 200:
                online_urls[url] = source_files
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
            pass
    return online_urls

print(
    '''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \     ransomwhat?      /  ************  \ 
    --------------------                    --------------------
    '''
)


# Process
onion_urls_dict = find_onion_urls(directory_to_search)
fqdn_set = get_fqdn_from_json(json_file_path)

# Identifying missing URLs and checking their online status
missing_urls_dict = {url: files for url, files in onion_urls_dict.items() if url not in fqdn_set}
if missing_urls_dict:
    stdlog("Checking online status for .onion URLs not present in groups.json...")
    online_urls = check_onion_urls_online(missing_urls_dict, exception_urls)
    for url, source_subdirectories in online_urls.items():
        source_files_str = f'[{source_subdirectories[0]}]' if source_subdirectories else '[Unknown]'
        print(f'{source_files_str} {url}')
else:
    stdlog("No new .onion URLs found outside of groups.json.")
