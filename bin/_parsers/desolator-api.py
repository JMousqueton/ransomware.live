#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests,os,re,pycountry
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import stdlog, errlog, appender

# Load env
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# Source URL
URL = "http://po4tq2brx4rgwbdx4mac24fz34uuuf7oigosebp32n2462m2vxl6biqd.onion"
API = URL + "/api/victims?page=1&rowsPerPage=50"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}


def fetch_data():
    try:
        r = requests.get(API, proxies=PROXIES, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        errlog(f"[{group_name}] ❌ Error fetching data: {e}")
        return {}

def convert_date(date_str):
    if not date_str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def clean_victim_name(display_name):
    if not display_name:
        return ""
    return re.sub(r"\s*\([^)]*\)\s*$", "", display_name).strip()

def extract_country_code(display_name):
    if not display_name:
        return ""
    match = re.search(r"\(([^)]+)\)\s*$", display_name)
    if not match:
        return ""
    country_name = match.group(1).strip()
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except LookupError:
        return country_name


def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')
    group_name = group_name.replace('-api','')

    data = fetch_data()
    if not data:
        return


    victims = data.get("victims", [])
    for entry in victims:
        victim = entry.get("display_name") or ""
        description = f"Status: {entry.get('status','')} | Expiration: {entry.get('expiration_date','')}"
        website = ""
        post_url = f"{URL}/victim/{entry.get('victim_id')}"
        published = convert_date(entry.get("infection_date")) or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        country = extract_country_code(entry.get("display_name")) or ""

        appender(
            victim=clean_victim_name(victim),
            group_name=group_name,
            description=description,
            website=website,
            published=published,
            post_url=post_url,
            country=country
        )


if __name__ == "__main__":
    main()
