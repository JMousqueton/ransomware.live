#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parser for ransomware.live
Gentlemen gang API
"""

import os
import re
import html
import requests
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import stdlog, errlog, appender

# ---------- ENV ----------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# ---------- SOURCE ----------
URL = "http://tezwsse5czllksjb7cwp65rvnk4oobmzti2znn42i43bjdfd2prqqkad.onion"
API = URL + "/api/companies"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}
TIMEOUT = 60

def sec_to_utc_str(sec_val) -> str:
    """epoch-seconds -> 'YYYY-MM-DD HH:MM:SS.ffffff' (UTC)."""
    try:
        if not sec_val:
            raise ValueError("empty")
        dt = datetime.fromtimestamp(int(sec_val), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

def compute_expiry_str(timer_start_sec, timer_hours) -> str:
    """(start in sec) + (hours) -> formatted UTC with microseconds."""
    try:
        start = int(timer_start_sec)
        hours = int(timer_hours)
        dt = datetime.fromtimestamp(start, tz=timezone.utc) + timedelta(hours=hours)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

def clean_desc(text: str) -> str:
    if not text:
        return ""
    t = html.unescape(text)
    t = re.sub(r"\r\n?", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def extract_first_fqdn(s: str) -> str:
    if not s:
        return ""


    m = re.search(r"\b(www\.[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b", s, flags=re.IGNORECASE)
    if m:
        return m.group(1).lower()

    m = re.search(r"(https?://[^\s,;]+)", s, flags=re.IGNORECASE)
    if m:
        try:
            return urlparse(m.group(1)).netloc.lower()
        except Exception:
            pass


    m = re.search(r"\b([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b", s)
    return m.group(1).lower() if m else ""


def fetch_data(group_name: str):
    try:
        r = requests.get(API, proxies=PROXIES, timeout=TIMEOUT)
        r.raise_for_status()
        js = r.json()
        if not isinstance(js, list):
            raise ValueError("unexpected JSON payload (expected list)")
        return js
    except Exception as e:
        errlog(f"[{group_name}] ❌ Error fetching data: {e}")
        return []

def main():
    # Resolve group_name from file (handles symlinks)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")
    group_name = group_name.replace("-api", "")

    records = fetch_data(group_name)
    if not records:
        return

    for entry in records:
        try:
            title = (entry.get("title") or "").strip()
            desc_raw = entry.get("description") or ""
            timer_start = entry.get("timerStart") or 0
            

            website_fqdn = extract_first_fqdn(desc_raw)
            description = clean_desc(desc_raw)

            added = sec_to_utc_str(timer_start)

            if description:
                description = description
            else:
                description_lines = "" 
            

            post_url = URL 
            published = added
            country = ""
            
            appender(
                victim=title,
                group_name=group_name,
                description=description,
                website=website_fqdn,
                published=published,
                post_url=post_url,
                country=country
                )
        except Exception as e:
            errlog(f"[{group_name}] ❌ Error parsing entry: {e}")

if __name__ == "__main__":
    main()
