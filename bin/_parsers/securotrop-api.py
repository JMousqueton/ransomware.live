#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parser for ransomware.live
Securo gang API
"""

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
URL = "http://securo45z554mw7rgrt7wcgv5eenj2xmxyrsdj3fcjsvindu63s4bsid.onion"
API = URL + "/api.php"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

TIMEOUT = 60


def ms_to_utc_str(ms_str: str) -> str:
    """Convert milliseconds epoch string to 'YYYY-MM-DD HH:MM:SS.ffffff' (UTC)."""
    try:
        if not ms_str:
            raise ValueError("empty")
        ms_int = int(ms_str)
        dt = datetime.fromtimestamp(ms_int / 1000.0, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")


def clean_desc(text: str) -> str:
    """Basic HTML -> plaintext normalization."""
    if not text:
        return ""
    t = re.sub(r"(?i)<br\s*/?>", "\n", text)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def clean_website(url: str) -> str:
    """Extract only FQDN from a URL."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        return parsed.netloc.lower()
    except Exception:
        return url.strip()


def fetch_data(group_name: str):
    try:
        r = requests.get(API, proxies=PROXIES, timeout=TIMEOUT)
        r.raise_for_status()
        js = r.json()
        if not isinstance(js, dict) or not js.get("status"):
            raise ValueError("unexpected JSON payload or status=false")
        return js.get("data", {})
    except Exception as e:
        errlog(f"[{group_name}] ❌ Error fetching data: {e}")
        return {}


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

    data = fetch_data(group_name)
    if not data:
        return

    companies = data.get("companies", [])
    if not isinstance(companies, list):
        errlog(f"[{group_name}] ❌ 'companies' not a list")
        return

    for entry in companies:
        try:
            name = (entry.get("name") or "").strip()
            is_published = bool(entry.get("is_published"))
            timer_expiry = ms_to_utc_str(entry.get("timer_expiry"))
            time_added = ms_to_utc_str(entry.get("time_added"))

            country = (entry.get("country") or "").strip().upper()
            website = clean_website(entry.get("website") or "")
            files_cnt = entry.get("files") or ""
            size_gb = entry.get("size") or ""
            employees = entry.get("employees") or ""
            revenue = entry.get("revenue") or ""
            views = entry.get("views")

            status_txt = "PUBLISHED" if is_published else "AWAITING"
            meta_bits = []
            #if employees: meta_bits.append(f"Employees: {employees}")
            #if revenue:   meta_bits.append(f"Revenue: {revenue}")
            #if files_cnt: meta_bits.append(f"Files: {files_cnt}")
            if size_gb:   meta_bits.append(f"Size: {size_gb} GB")
            #if views is not None: meta_bits.append(f"Views: {views}")

            details = clean_desc(entry.get("description") or "")
            meta_line = " | ".join(meta_bits) if meta_bits else ""
            description_lines = [f"Status: {status_txt}"]
            if meta_line:
                description_lines.append(meta_line)
            #description_lines.append(f"Added: {time_added}")
            #description_lines.append(f"Timer expiry: {timer_expiry}")
            #if details:
            #    description_lines.append("")
            #    description_lines.append(details)
            description = "\n".join(description_lines).strip()

            cid = (entry.get("id") or "").strip()
            post_url = URL
            published = time_added
            appender(
                victim=name,
                group_name=group_name,
                description=description,
                website=website,
                published=published,
                post_url=post_url,
                country=country,
                extra_infos={"data_size": f"{size_gb} GB"},
            )
            """
            print('victim:', name)
            print('description:', description)
            print('website:', website)
            print('published:', published) 
            print('post_url:', post_url)
            print('country:', country)
            print('data_size:', f"{size_gb} GB")
            print('-'*40)
            """
        except Exception as e:
            errlog(f"[{group_name}] ❌ Error parsing entry: {e}")


if __name__ == "__main__":
    main()
