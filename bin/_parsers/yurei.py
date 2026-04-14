#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for Yurei Blog listing cards.

Expect structure:
  <a class="leak-card" href="/blog/<slug>/">
    <h5>Victim Name</h5>
    <p>Description...</p>
  </a>

Behavior:
  - Scans $RANSOMWARELIVE_HOME$TMP_DIR for files starting with "<group_name>-"
  - Extracts victim (h5), description (first <p>)
  - post_url is derived from find_slug_by_md5(group_name, extract_md5_from_filename(file))
  - Appends via shared_utils.appender with empty website/published/country

Dependencies in shared_utils:
  - appender
  - errlog
  - find_slug_by_md5
  - extract_md5_from_filename
"""

import os, sys
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from shared_utils import appender, errlog, find_slug_by_md5, extract_md5_from_filename

# ---------- ENV ----------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME") or ""
tmp_dir = Path(home + (os.getenv("TMP_DIR") or ""))

def main():
    # Deduce group_name from filename (supports symlinked script)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    # Iterate over captured HTML files for this group
    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Compute post_url once per file from its md5 filename
            url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

            # Each card is an <a.leak-card>
            for a in soup.select("a.leak-card"):
                # Victim name
                h5 = a.find("h5")
                victim = h5.get_text(strip=True) if h5 else "N/A"

                # Description: first <p> inside the anchor
                p = a.find("p")
                description = p.get_text(" ", strip=True) if p else ""

                href = a.get("href") or ""

                post_url = url + href if url and href else ""

                # Fields not present on the list page
                website = ""
                published = ""   # no date on listing; keep blank
                country = ""     # not exposed here
                
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website=website,
                    published=published,
                    post_url=post_url,
                    country=country
                )
                """
                print('Victim:', victim)
                print('Description:', description)
                print('Post URL:', post_url)
                print('_' * 40)
                """
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {str(e)} in file: {filename}")

if __name__ == "__main__":
    main()
