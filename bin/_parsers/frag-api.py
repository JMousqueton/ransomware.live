import requests
from urllib.parse import urljoin
from datetime import datetime
from shared_utils import appender


# Configuration
base_url = "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion"
endpoint = "/tada/posts/leaks?page="
tor_proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

extracted_data = []

def fetch_page(page_number):
    url = f"{base_url}{endpoint}{page_number}"
    response = requests.get(url, proxies=tor_proxies, timeout=30)
    response.raise_for_status()
    return response.json()

def convert_date(date_str):
    # Parse ISO string with milliseconds and Zulu timezone
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def main():
    # Get first page to determine total pages
    first_page = fetch_page(1)
    total_items = first_page["total"]
    per_page = first_page["perPage"]
    total_pages = (total_items + per_page - 1) // per_page

    # Process all pages
    for page in range(1, total_pages + 1):
        data = fetch_page(page)
        for item in data["items"]:
            appender(item["title"].split("|")[0].strip(),'frag',item["text"],'',convert_date(item["date"]))


