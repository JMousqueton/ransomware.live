import requests
from shared_utils import msgtoPushover

# Define the URL
onion_url = "http://owt3kwkxod2pvxlv3uljzskfhebhrhoedrh5gqrxyyd6rrco4frzj5ad.onion/api/posts"

# Use the Tor network for routing requests
proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

def main():
    try:
        response = requests.get(onion_url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            if json_data:  # Check if the response is not empty
                msgtoPushover("MAMONA VICTIM DETECTED !!!")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
