import requests
import json

# Define the request URL and payload
url = "http://www.bing.com/IndexNow"  # Replace <searchengine> with the actual search engine host
payload = {
    "host": "www.ransomware.live",
    "key": "6a70e4ea73834288ba42618200e262c7",
    "keyLocation": "https://www.ransomware.live/6a70e4ea73834288ba42618200e262c7.txt",
    "urlList": [
        "https://www.ransomware.live/#/negotiations",
        "https://ransomware.live/#/recentcyberattacks"
    ]
}

# Set the headers
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Host": "www.bing.com"  # Replace <searchengine> with the actual search engine host
}

# Send the POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Check the response status code
if response.status_code == 200:
    print("Request succeeded!")
else:
    print(f"Request failed with status code {response.status_code}.")

