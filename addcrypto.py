import requests
import json
from datetime import datetime as dt
from sharedutils import stdlog, errlog
import os

def writeline(file, line):
    '''write line to file'''
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.close()

url = "https://api.ransomwhe.re/export"

NowTime=dt.now() 

# Fetch the JSON data from the URL
response = requests.get(url)
response.raise_for_status()
result = response.json()

# Load the other JSON file
with open("groups.json") as json_file:
    groups = json.load(json_file)

for group in groups:
    keep = False
    stdlog(group["name"] + ' : analyze crypto')
    cryptofile='docs/crypto/'+ group["name"] +'.md'
    with open(cryptofile, 'w', encoding='utf-8') as f:
        f.close()
    writeline(cryptofile,'# ' + group["name"] + ' : Crypto wallet(s)')
    writeline(cryptofile,'')
    writeline(cryptofile,'| address | blockchain | Balance |')
    writeline(cryptofile, '|---|---|---|')
    # Sort the result list by family
    result["result"].sort(key=lambda x: x.get("family", ""))

    # Iterate through the sorted result list
    for address_info in result["result"]:
        family = address_info.get("family", "").split(" ", 1)[0].lower()
        # print(family)
        if family == group["name"]:
            keep = True 
            url = address_info['address']
            if address_info['blockchain'] == "bitcoin":
                url='[' + address_info['address'] + '](https://www.blockchain.com/explorer/addresses/btc/' + address_info['address'] + ')'
            writeline(cryptofile, '| ' + url + ' | ' + address_info['blockchain'] + ' | $ ' + str(round(float(address_info['balanceUSD']))) + ' |')
    writeline(cryptofile, '')
    writeline(cryptofile, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    writeline(cryptofile, '')
    if keep == False:
        os.remove(cryptofile)