# The following code grabs the data from the "Recent Victims" Tab. The code will check if there is an associated domain present for the victim, if yes, it'll add it to the final list - victim_git_final.csv. In case if the domain is not present, it'll check for the corresponding company name, perform a google search and grab the first url. It'll then extract the domain from the url and finally present you with a list of domains for all recent victims

# There is also a function defined to calculate previous month and year based on the "current date" when the script is executed and that can be used to get data for tha specific month and year instead of all Recent victims. use the url specified on line 85 for this fucntion

##############################################################
# You might need to verify the value of the class specified on line 54. in case it's different update that value and the code should work as intended. this should be a one time change if at all required
# Since there are multiple class values when inspecting the data stored in the 'soup' variable, we want the value where in the url of the google search results associated with the company name is stored
##############################################################

import requests
import tldextract
import json
import pandas as pd
import time
from requests.exceptions import HTTPError, ProxyError
from bs4 import BeautifulSoup

# Defines the order in which the data will be stored in the csv file
column_order = ['post_title','group_name','discovered','published','post_url','country','website']

# Function to calculate the previous month and year based on the current date
'''def get_year_and_prev_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    year = int(last_month.strftime("%Y"))
    prev_month = int(last_month.strftime("%m"))
    return (year, prev_month)'''

# Checks if the name is in url format then extracts the domain from it
def get_domain(url):
    extracted = tldextract.extract(url)
    domain = extracted.domain + '.' + extracted.suffix
    return domain

# Extracts the domain name from the url retrieved after performing a google search for the company name
def get_domain_post_title(url):
    if url == "N/A":
        return url
    else:
        url = url.split('?q=')[1]
        extracted = tldextract.extract(url)
        domain = extracted.domain + '.' + extracted.suffix
        return domain

# Google search the company name to extract the associated domain name
def google_search(query):
    try:
        
        url = f"https://www.google.com/search?q={'+'.join(query.split())}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='egMi0 kCrYT')
        
        if search_results:
            first_link = (search_results[0].find('a'))['href']
            return first_link     
        else: 
            print("No results found")
            first_link = "N/A"
            return first_link
        
    except HTTPError as e:
        if e.response.status_code == 429:
            print("Too many requests, Retrying in 120 seconds..")
            time.sleep(600)
            return google_search(query)
        else:
            print(f"HTTP Error: {e.response.status_code}")

    except ProxyError as pe:
        print(f"Proxy error: {pe}")

    except requests.exceptions.ReadTimeout:
        print("Timeout occurred")

    except StopIteration:
        return None

# Get the data from the api and format the data into a csv file
def main():
    #year, prev_month = get_year_and_prev_month()
    url = 'https://api.ransomware.live/recentvictims'
    #url = f'https://api.ransomware.live/victims/{year}/{prev_month}'
    #url = 'https://data.ransomware.live/posts.json'
    response = requests.get(url)
    if response:
        json_data = json.loads(response.text)
        
        # If the data already contains a domain name associated, use that else perform a google search
        for data in json_data:
            if 'website' in data and data['website']:
                data['website'] = get_domain(data['website'])
            else:
                search_result = google_search(data['post_title'])
                if search_result is not None:
                    data['website'] = get_domain_post_title(search_result)

            time.sleep(5)
            
            # Standardize the format in which the data is stored and deduplicate results
            df = pd.DataFrame([data])
            df = df[column_order]

            df.to_csv('victim_git_final.csv', mode='a', encoding='utf-8', index=False, header=False)

    df = pd.read_csv('victim_git_final.csv')
    df_dedup = df.drop_duplicates(subset=['post_title','published'])
    df_dedup.to_csv('victim_final.csv', index=False)


if __name__ == "__main__":
    main()
