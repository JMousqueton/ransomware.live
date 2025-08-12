import requests
import json
from datetime import datetime
from shared_utils import stdlog, errlog, appender # Importing stdlog for standard logs and errlog for errors

# Define the API URL (Requires a Tor proxy)
API_URL = "http://7i6sfmfvmqfaabjksckwrttu3nsbopl3xev2vbxbkghsivs5lqp4yeqd.onion:8088/api/v1/product?page=1&pageSize=20"
LINK_URL = "http://7i6sfmfvmqfaabjksckwrttu3nsbopl3xev2vbxbkghsivs5lqp4yeqd.onion"

# Define the Tor proxy (Adjust as necessary)
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

def fetch_data():
    try:
        stdlog(f"Fetching data from {API_URL} via Tor proxy...")
        response = requests.get(API_URL, proxies=PROXIES, timeout=30)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()
        
        if data.get("code") == 0 and "list" in data["data"]:
            stdlog(f"Successfully retrieved {len(data['data']['list'])} products.")
            return data["data"]["list"]
        else:
            errlog("Unexpected response format:")
            errlog(json.dumps(data, indent=4))
            return []

    except requests.RequestException as e:
        errlog(f"Error fetching data: {e}")
        return []

def convert_timestamp(iso_timestamp):
    """Convert ISO 8601 timestamp to 'YYYY-MM-DD HH:MM:SS.ssssss' format."""
    try:
        dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")  # Output format
    except ValueError:
        errlog(f"Timestamp conversion failed for: {iso_timestamp}")
        return iso_timestamp  # Return original if conversion fails

def clean_name(name):
    """Remove 'Taiwan - ' prefix from the product name."""
    return name.split("-", 1)[-1].strip() if "-" in name else name

def main():
    products = fetch_data()
    
    if not products:
        errlog("No products found.")
        return

    for product in products:
        '''print(f"ID: {product['ID']}")
        print(f"Link: {LINK_URL}/product/{product['ID']} ")
        print(f"Name: {product['productName']}")
        print(f"Price: {product['productPrice']}")
        print(f"Description: {product['productDesc']}")
        print(f"Sold Out: {product['productSoldOut']}")
        print(f"Created At: {product['CreatedAt']}")
        print(f"Expires At: {product['expiredAt']}")
        print("-" * 40)  # Separator for better readability
        '''
        ransom = product['productPrice']
        extra_infos = { 'ransom': ransom }
        appender(clean_name(product['productName']),'crazyhunter',product['productDesc'],'',convert_timestamp(product['CreatedAt']),LINK_URL+"/product/"+str(product['ID']),'',extra_infos)
if __name__ == "__main__":
    main()

