#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import html
import requests
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import stdlog, errlog, appender

# ---------- ENV ----------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# ---------- SOURCE ----------
URL = "http://3bnusfu2lgk5at43ceu7cdok5yv4gfbono2jv57ho74ucjvc7czirfid.onion"
APIS = [URL + "/api/leakeds_a", URL + "/api/leakeds_u"]

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}
TIMEOUT = 60

# ---------- HELPERS ----------
def clean_text(t: str) -> str:
    if not t:
        return ""
    t = html.unescape(t)
    t = re.sub(r"\r\n?", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def normalize_published(created_at: str) -> str:
    """
    Input example: '2025-09-10 15:11:42'
    Output: 'YYYY-MM-DD HH:MM:SS.ffffff' (UTC)
    """
    if not created_at:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
    created_at = created_at.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            dt = datetime.strptime(created_at, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            continue
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

def fetch_data(api: str, group_name: str):
    try:
        r = requests.get(api, proxies=PROXIES, timeout=TIMEOUT)
        r.raise_for_status()
        js = r.json()
        if js is None:
            stdlog(f"[{group_name}] no records (null) from {api}")
            return []
        if not isinstance(js, list):
            raise ValueError("unexpected JSON payload (expected list)")
        stdlog(f"[{group_name}] fetched {len(js)} records from {api}")
        return js
    except Exception as e:
        errlog(f"[{group_name}] ❌ Error fetching {api}: {e}")
        return []


# ---------- MAIN ----------
def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")
    group_name = group_name.replace("-api", "")


    for api in APIS:
        records = fetch_data(api, group_name)
        for entry in records:
            try:
                victim = (entry.get("company_name") or "").strip()
                desc = clean_text(entry.get("description") or entry.get("blog") or "")
                website_raw = (entry.get("website") or "").strip()
                website_fqdn = (
                    urlparse(website_raw).netloc.lower()
                    if website_raw.startswith(("http://", "https://"))
                    else ""
                )
                published = normalize_published(entry.get("created_at") or "")

                appender(
                    victim=victim,
                    group_name=group_name,
                    description=desc,
                    website=website_fqdn,
                    published=published
                )

            except Exception as e:
                errlog(f"[{group_name}] ❌ Error parsing id={entry.get('id')}: {e}")

if __name__ == "__main__":
    main()