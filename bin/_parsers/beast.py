#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parser for: BEAST LEAKS | Index
Extracts per card: victim (h3), description, website, published ("Published" or ""),
post_url (absolute). Country not present → "".
"""

import os
from pathlib import Path
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

from shared_utils import (
    find_slug_by_md5,
    appender,
    extract_md5_from_filename,
    errlog,
)

# ---------- Env ----------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def get_origin(url: str) -> str:
    """Return scheme://netloc for a URL, else empty string."""
    try:
        p = urlparse(url)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}"
    except Exception:
        pass
    return ""

def parse_file(html_path: Path, group_name: str):
    """Parse a saved BEAST LEAKS index HTML and call appender() per card."""
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
    except Exception as e:
        errlog(f"{group_name} - failed to open/parse {html_path.name}: {e}")
        return

    # Basic guard: ensure page title matches
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if title != "BEAST LEAKS | Index":
        return

    # Base origin from stored slug (so we can absolutize /card/... links)
    slug_url = find_slug_by_md5(group_name, extract_md5_from_filename(html_path.name))
    origin = get_origin(slug_url)

    # Each card is an <a class="card ..."> inside .catalog
    for a in soup.select("div.catalog a.card"):
        try:
            # Victim / title
            h3 = a.select_one(".card-head h3")
            victim = (h3.get_text(" ", strip=True) if h3 else "").strip()

            # Description (all text inside .card-text)
            card_text = a.select_one(".card-text")
            description = card_text.get_text(" ", strip=True) if card_text else ""

            # Website
            website_span = a.select_one(".card-info .website")
            website = website_span.get_text(strip=True) if website_span else ""

            # Data size
            size_span = a.select_one(".card-info .size")
            data_size = size_span.get_text(strip=True) if size_span else ""
            extra_infos = { "data_size": data_size }

            # Published date (normalize)
            published = ""
            date_span = a.select_one(".card-info .date")
            if date_span:
                raw_date = date_span.get_text(strip=True)
                for fmt in ("%d.%m.%Y", "%Y.%m.%d", "%d.%m.%y", "%m.%d.%Y"):
                    try:
                        dt = datetime.strptime(raw_date, fmt)
                        published = dt.strftime("%Y-%m-%d 00:00:00.000000")
                        break
                    except ValueError:
                        continue


            # Post URL (absolutize)
            href = a.get("href", "").strip()
            post_url = urljoin(origin + "/", href) if origin else href

            if victim:
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website=website,
                    published=published,
                    post_url=post_url,
                    country="",  # not available on this page
                    extra_infos=extra_infos
                )
        except Exception as e:
            errlog(f"{group_name} - card parse error in {html_path.name}: {e}")

def main():
    # Determine ransomware group name from script filename or symlink target
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(os.path.abspath(original_path)).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    try:
        for filename in os.listdir(tmp_dir):
            if not filename.startswith(group_name + "-"):
                continue
            html_path = tmp_dir / filename
            parse_file(html_path, group_name)
    except Exception as e:
        errlog(f"{group_name} - parsing fail with error: {e}")

if __name__ == "__main__":
    main()
