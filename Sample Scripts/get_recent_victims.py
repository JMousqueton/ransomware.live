# The following code grabs the data from the "Recent Victims" Tab. The code will check if there is an associated domain present for the victim, if yes, it'll add it to the final list - results.json. In case if the domain is not present, it'll check for the corresponding company name, perform a google search and grab the first url. It'll then extract the domain from the url and finally present you with a list of domains for all recent victims

import requests
import tldextract
from googlesearch import search
import json
import os

def is_domain(name):
    tld_info = tldextract.extract(name)
    return bool(tld_info.domain and tld_info.suffix)

def get_domain(url):
    extracted = tldextract.extract(url)
    domain = extracted.domain + '.' + extracted.suffix
    return domain

def google_search(query):
    try:
        return next(search(query, num_results=1))
    except StopIteration:
        return None

def main():
    victims=[]
    url = 'https://api.ransomware.live/recentvictims'
    response = requests.get(url)
    if response:
        json_data = json.loads(response.text)
        for data in json_data:
            if data['website']:
                victims.append(data['website'])
            else:
                victims.append(data['post_title'])
    result = []
    for victim in victims:
        if is_domain(victim):
            result.append(get_domain(victim))
        else:
            search_result = google_search(victim)
            if search_result is not None:
                result.append(get_domain(search_result))

    if os.path.exists('result.json'):
        with open('result.json', 'r') as f:
            old_result = json.load(f)
        result = old_result + result

    with open('result.json', 'w') as f:
        json.dump(result, f)

    print(result)
if __name__ == "__main__":
    main()
