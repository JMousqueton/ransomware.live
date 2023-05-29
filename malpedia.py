#!/usr/bin/env python3
import json
import re
import requests
from sharedutils import openjson

response =  requests.get('https://malpedia.caad.fkie.fraunhofer.de/api/get/families')
if response.status_code != 200:
    print(response.text)
    exit(0)

families = json.loads(response.text)
groups = openjson("groups.json")

for family in families:
    names = []
    names.append(families[family]['common_name'])
    names.extend(families[family]['alt_names'])
    names = [x.lower() for x in names]
    #print(family)
    #print(names)
    for group in groups:
            if group.get('description') is None:
                if group['name'] in names:
                    if families[family]['description'].lower() != "ransomware.":
                        group['description'] = re.sub(r'[\n\t\r]', '', families[family]['description'])
                        print(group['name'] + ' --> ' + group['description'])
                
#with open('groups.json', 'w', encoding='utf-8') as groupsfile:
#    json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
#groupsfile.close()
       
