#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parser for: Safepay Blog (cards grid)
Extracts: victim/domain, description, website, post_url, country
"""

import os, sys, re
from pathlib import Path
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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

FLAG_RE = re.compile(r"/(\d+x\d+)/([a-z]{2})\.png$", re.I)

def get_origin(url: str) -> str:
    """Return scheme://netloc for a URL, else empty string."""
    try:
        p = urlparse(url)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}"
    except Exception:
        pass
    return ""

def extract_country_code(img) -> str:
    """Extract 2-letter country code from <img class='country-flag'>."""
    if not img:
        return ""
    # Prefer alt if present
    alt = (img.get("alt") or "").strip()
    if alt and len(alt) in (2, 3):  # e.g., 'US', 'GB'
        return alt.upper()
    # Fallback to src path pattern .../16x12/us.png
    src = img.get("src") or ""
    m = FLAG_RE.search(src)
    if m:
        return m.group(2).upper()
    return ""

def parse_file(html_path: Path, group_name: str):
    """Parse a single saved HTML and call appender() per card/post."""
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
    except Exception as e:
        errlog(f"{group_name} - failed to open/parse {html_path.name}: {e}")
        return

    # Page identity
    page_title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    if page_title != "Safepay Blog":
        # Not our target page
        return

    # Build an origin (scheme://host) from the saved page slug
    slug_url = find_slug_by_md5(group_name, extract_md5_from_filename(html_path.name))
    origin = get_origin(slug_url)

    cards = soup.select("div.card.h-100")
    for card in cards:
        try:
            # Victim / domain (in <h5 class="card-title">)
            h5 = card.select_one("h5.card-title")
            victim = (h5.get_text(strip=True) if h5 else "").strip()

            # Description (first <p class="card-text">)
            p = card.select_one("div.card-body p.card-text")
            description = (p.get_text(separator=" ", strip=True) if p else "")

            # Country (from <img class="country-flag">)
            country_img = card.select_one("img.country-flag")
            country = extract_country_code(country_img)

            # Website (same as victim/domain text)
            website = victim

            # Post URL (from "Learn More" button in card-footer)
            learn_more = card.select_one("div.card-footer a[href]")
            post_href = learn_more["href"].strip() if learn_more and learn_more.has_attr("href") else ""
            # Absolutize using origin if href is root-relative
            post_url = urljoin(origin + "/", post_href) if origin else post_href

            # Append record
            if victim:
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website=website,
                    published="",
                    post_url=post_url,
                    country=country,
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

    # Walk tmp_dir for files starting with '<group_name>-'
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
