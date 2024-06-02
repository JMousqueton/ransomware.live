import requests
import json
import re
import argparse
from datetime import datetime
import os
import time
from sharedutils import stdlog, dbglog, errlog 
from urllib.parse import urlparse
import hashlib
from dotenv import load_dotenv



def parse_arguments():
    parser = argparse.ArgumentParser(description="Script to query and update domain information related to info-stealers.")
    parser.add_argument('-F', '--force', action='store_true', help='Force update the existing data for domains.')
    return parser.parse_args()

def is_valid_domain(domain):
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None

def extract_domain(url):
    if '://' not in url:
        url = 'http://' + url  # Assumption to handle URLs without a scheme
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc.replace('www.','')
    return ''

def query_users_api(domain):
    #url = "https://cavalier.hudsonrock.com/api/json/v2/stats/website-results"
    url = "https://cavalier.hudsonrock.com/api/json/v2/search-by-domain/assessment"
    api_key = os.getenv('HR_API_KEY')
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {'domain': domain}
    response = requests.post(url, json=data, headers=headers)
    return response

def query_urls_api(domain):
    url = "https://cavalier.hudsonrock.com/api/json/v2/search-by-domain/discovery"
    api_key = os.getenv('HR_API_KEY')
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {'domain': domain}
    response = requests.post(url, json=data, headers=headers)
    return response

def save_to_json(domain, employees, users, third_parties, employees_url, users_url, existing_data):
    data_to_save = {
        "update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "employees": employees,
        "users": users,
        "thirdparties": third_parties,
        "employees_url": employees_url,
        "users_url": users_url
    }
    existing_data[domain] = data_to_save

    with open('hudsonrock.json', 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

def load_existing_data():
    if os.path.exists('hudsonrock.json'):
        with open('hudsonrock.json', 'r') as json_file:
            return json.load(json_file)
    return {}

def is_current_year(discovered_date):
    discovered_year = datetime.strptime(discovered_date, "%Y-%m-%d %H:%M:%S.%f").year
    return discovered_year == datetime.now().year
    #return True

def is_current_year_and_month(discovered_date):
    discovered_datetime = datetime.strptime(discovered_date, "%Y-%m-%d %H:%M:%S.%f")
    current_datetime = datetime.now()
    return discovered_datetime.year == current_datetime.year and discovered_datetime.month == current_datetime.month


def write_markdown(domain, employees, users, third_parties, employees_url, users_url, update):
    # Generate MD5 hash of the domain
    md5_hash = hashlib.md5(domain.encode()).hexdigest()
    file_path = f"./docs/domain/{md5_hash}.md"

    # Ensure the directories exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if float(employees) > 0:
        employees = '`'+str(employees)+'`'
    if float(users) > 0:
        users = '`'+str(users)+'`'
    if float(third_parties) > 0:
        third_parties = '`'+str(third_parties)+'`'
    if float(employees_url) > 0:
        employees_url = '`'+str(employees_url)+'`'
    if float(users_url) > 0:
        users_url = '`'+str(users_url)+'`'

    # Markdown content
    markdown_content = f"""## Information for domain: **{domain}**

![logo {domain}](https://logo.clearbit.com/{domain} ":no-zoom")

> [!INFO] `Information stealer` (infostealer) is a malware—malicious software designed to steal victim information, including passwords

The corporate infrastructure for `{domain}` could have been compromised by Infostealer.

#### Compromised Credentials<sup>1</sup>

| Compromised Employees | Compromised Users | 
| ---- | ---- |
| {employees} | {users} |

#### External surface attack<sup>2</sup> 

| Employee URLs | Users URLs | 
| ---- | ---- |
| {employees_url} | {users_url} | 


> This information is provided by [HudsonRock](https://hudsonrock.com/search?domain={domain})

> [!TIP]
> (1) **Compromised credentials** of employees, partners and customers.
>
> (2) **External surface attack** : Discovered IT services that hackers could use to infiltrate the company and put it at risk.
 

* Data information : {update}
"""

    # Write to Markdown file
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)
    stdlog(f"Markdown file created for domain {domain}: {file_path}")


def main():
    # Load environment variables from .env file
    load_dotenv()
    args = parse_arguments()
    start_time = datetime.now()  # Capture start time
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

    existing_data = load_existing_data()

    try:
        with open('posts.json', 'r') as file:
            posts = json.load(file)
    except Exception as e:
        stdlog(f"Failed to load posts.json: {e}")
        return

    for post in posts:
        post_title = post.get("post_title", "").lower()
        discovered_date = post.get("discovered", "")
        website_url = post.get("website", "").strip().lower()
        domain_to_query = ''
        
        if is_valid_domain(post_title):
            domain_to_query = post_title.lower().replace('www.','')
        elif website_url:
            domain = extract_domain(website_url)
            if is_valid_domain(domain):
                domain_to_query = domain.lower()

        if len(domain_to_query) > 3 and is_current_year(discovered_date): # and is_current_year_and_month(discovered_date):  
            if args.force or domain_to_query not in existing_data:
                stdlog(f"Querying Users API for domain: {domain_to_query}")
                response_users = query_users_api(domain_to_query)
                if response_users.status_code == 200:
                    response_users_data = response_users.json()
                    employees = response_users_data['data'].get('employees_count', 0)
                    users = response_users_data['data'].get('users_count', 0)
                
                stdlog(f"Querying URLs API for domain: {domain_to_query}")
                response_urls = query_urls_api(domain_to_query)
                if response_urls.status_code == 200:
                    response_urls_data = response_urls.json()
                    employees_url = 0 
                    employees_url = len(response_urls_data["data"]["employees_urls"])
                    clients_url = 0 
                    clients_url = len(response_urls_data["data"]["clients_urls"])
                    third_parties = 0
                    third_parties = len(response_urls_data["data"]["third_party_urls"])

                    stdlog(f"Domain: {domain_to_query}, Employees: {employees}, Users: {users}, Third Parties: {third_parties}")
                    save_to_json(domain_to_query, employees, users, third_parties, employees_url, users_url, existing_data)
                    if employees > 0 or users > 0 or third_parties > 0:
                        write_markdown(domain_to_query, employees, users, third_parties,employees_url, users_url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    stdlog(f"Failed to fetch data for domain '{post_title}', status code: {response.status_code}")
                
                time.sleep(6)
            else:
                stdlog(f"Data for domain '{domain_to_query}' already exists. Generating Markdown file.")
                domain_data = existing_data[domain_to_query]
                employees = domain_data.get("employees", 0)
                users = domain_data.get("users", 0)
                third_parties = domain_data.get("thirdparties", 0)
                update = domain_data.get("update",0)
                employees_url = domain_data.get("employees_url",0)
                users_url = domain_data.get("users_url",0)
                if employees > 0 or users > 0 or third_parties > 0:
                    write_markdown(domain_to_query, employees, users, third_parties, employees_url, users_url, update)
        
        
    end_time = datetime.now()  # Capture end time
    duration = end_time - start_time  # Calculate duration
    stdlog("Script execution time: " + str(duration.total_seconds()) + " seconds")

if __name__ == "__main__":
    main()
