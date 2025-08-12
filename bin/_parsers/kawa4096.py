import os
import re
import json
import requests
import random
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from shared_utils import  appender

# Chargement .env si défini
load_dotenv(dotenv_path=Path("../.env"))
home = os.getenv("RANSOMWARELIVE_HOME", ".")
group_name = "kawa4096"

# Configuration Tor
base_url = "http://kawasa2qo7345dt7ogxmx7qmn6z2hnwaoi3h5aeosupozkddqwp6lqqd.onion"
tor_proxy = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

def fetch_main_page():
    print(f"[+] Fetching {group_name} main page...")
    r = requests.get(base_url, proxies=tor_proxy, timeout=30)
    r.raise_for_status()
    return r.text

def extract_js_url(html):
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", src=True):
        if "leaks-data" in script["src"]:
            js_path = script["src"]
            full_url = base_url + js_path if js_path.startswith("/") else js_path
            print(f"[+] Found JS URL: {full_url}")
            return full_url
    raise ValueError("Leak JS URL not found")

def fetch_js_content(js_url):
    print(f"[+] Fetching leak JS content...")
    r = requests.get(js_url, proxies=tor_proxy, timeout=30)
    r.raise_for_status()
    return r.text

def convert_to_full_datetime(date_str):
    try:
        base_date = datetime.strptime(date_str, "%Y-%m-%d")
        full_dt = base_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=random.randint(0, 999999)
        )
        return full_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return date_str

def parse_leaks(js_content):
    match = re.search(r"leaks\s*=\s*(\[\{.*?\}\])", js_content)
    if not match:
        raise ValueError("Unable to extract leaks array from JS.")

    leaks_raw = match.group(1)
    leaks_json_compatible = re.sub(r'([{,])(\s*)(\w+):', r'\1"\3":', leaks_raw)
    leaks = json.loads(leaks_json_compatible)

    for leak in leaks:
        leak["group"] = group_name
        try:
            leak["full_url"] = base_url + leak["url"]
        except:
            leak["full_url"] = ""
        leak["date"] = convert_to_full_datetime(leak.get("date", ""))

        # Extraction country / name
        title = leak.get("title", "")
        if ":" in title:
            leak["country"], leak["name"] = title.split(":", 1)
        else:
            leak["country"] = ""
            leak["name"] = title

    return leaks

def main():
    try:
        html = fetch_main_page()
        js_url = extract_js_url(html)
        js_content = fetch_js_content(js_url)
        leaks = parse_leaks(js_content)

        for leak in leaks:
            """
            print("-----")
            print(f"victim: {leak.get('title')}")
            print(f"country: {leak.get('country')}")
            print(f"name: {leak.get('name')}")
            print(f"description: {leak.get('description')}")
            print(f"date: {leak.get('date')}")
            print(f"url: {leak.get('url')}")
            print(f"group: {leak.get('group')}")
            print(f"full_url: {leak.get('full_url')}")
            print("")
            """
            appender(
                            victim=leak.get('name'),
                            group_name=group_name,
                            description=leak.get('description'),
                            website="",
                            published=leak.get('date'),
                            post_url=leak.get('full_url'),
                            country=leak.get('country')
                        )

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
