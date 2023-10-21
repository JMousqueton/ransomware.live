import requests
import socks
import json
from sharedutils import stdlog, dbglog, errlog   # , honk
from sharedutils import openjson
from datetime import datetime
from parse import appender
import urllib3

onion_url= 'https://hunters55rdxciehoqzwv7vgyv6nt37tbwax2reroyzxhou7my5ejyid.onion/api/public/companies'

# Disable the warning about certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def get_country(id):
# Define the base URL of the API and the endpoint
    base_url = "https://api.ransomware.live"  # Replace with the actual API base URL
    endpoint = f"/country/{id}"  # Replace with the actual endpoint

    # Send a GET request to the API endpoint
    response = requests.get(f"{base_url}{endpoint}")

    # Check the response status code
    if response.status_code == 200:
        # The request was successful, and we can extract the country name from the JSON response
        data = response.json()
        country_name = data.get("title")
        return country_name
    elif response.status_code == 404:
        # The API returned a 404 error, which means the country was not found
        return "N/A"
    elif response.status_code == 500:
        # The API returned a 500 error, which means the country was not found
        return "N/A"
    else:
        # Handle other HTTP status codes as needed
        return "Internal Error"

def existingpost(post_title, group_name):
    '''
    check if a post already exists in posts.json
    '''
    posts = openjson('posts.json')
    # posts = openjson('posts.json')
    for post in posts:
        if post['post_title'].lower() == post_title.lower() and post['group_name'] == group_name:
            return True
    return False

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

def convert_date(unix_timestamp):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(unix_timestamp)
    # Format the datetime object as a string with microseconds
    formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime

def convert_text(txt):
    if txt == True:
        return "yes"
    else:
        return "no"

def main():

    json_data = fetch_json_from_onion_url(onion_url)
    if json_data is not None:
        for item in json_data:
            title = item['title'].strip()
            country = get_country(item['country'])
            website = item['website']
            exfiltration = item['exfiltrated_data']
            encryption = item['encrypted_data']
            published = item['updated_at']
            description = "Country : " +  country + " - Exfiltraded data : " + convert_text(exfiltration) +  " - Encrypted data : " + convert_text(encryption)
            appender(title, 'hunter', description,convert_date(published), website)
