import json
import requests

# Load the JSON data from the file
with open('groups.json') as file:
    data = json.load(file)

# Iterate over the groups
for group in data:
    # Extract the name variable from the group
    name = group['name']

    # Find the available location within the group
    available_location = next((location for location in group['locations'] if location.get('available', False)), None)

    if available_location:
        # Extract the URL from the available location
        url = available_location['slug']

        # Set up the session to use the Tor SOCKS proxy
        requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://localhost:9050',
            'https': 'socks5h://localhost:9050'
        }

        # Make the request and retrieve the response headers
        try:
            response = session.head(url, verify=False)

            # Extract the server header from the response headers
            server_header = response.headers.get('Server', '')

            print(f"{name},{server_header}")
        except: 
            pass
    
    #else:
    #    print(f"No available location found for group: {name}")

