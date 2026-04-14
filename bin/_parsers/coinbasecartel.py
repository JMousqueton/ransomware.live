#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal parser for Coinbasecartel (new layout)
- Parses company rows from the Companies list
- Extracts victim, detail URL, website, optional description
- Matches ransomware.live minimal ingestion style
"""

import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

BASE_URL = os.getenv(
    "BASE_URL",
    "http://fjg4zi4opkxkvdz7mvwp7h6goe4tcby3hhkrz43pht4j3vakhy75znyd.onion"
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _group_name_from_self() -> str:
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        return os.path.basename(original_path).replace(".py", "")
    return os.path.basename(script_path).replace(".py", "")


def _normalize_post_url(href: str) -> str:
    if not href:
        return ""
    if href.startswith("/"):
        return BASE_URL.rstrip("/") + href
    return href


# ------------------------------------------------------------
# Main parser
# ------------------------------------------------------------
def main():
    group_name = _group_name_from_self()

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + "-"):
            continue

        try:
            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Featured description (only appears once)
            featured_desc = ""
            featured = soup.select_one("article.company-row-featured")
            if featured:
                desc = featured.select_one(".company-row-desc")
                if desc:
                    featured_desc = desc.get_text(" ", strip=True)

            # All company rows
            rows = soup.select("article.company-row")
            for row in rows:
                # Victim name
                name_tag = row.select_one("h3.company-name")
                victim = name_tag.get_text(strip=True) if name_tag else "N/A"

                # Detail URL
                link_tag = row.select_one(".company-row-actions a.btn-primary[href]")
                post_url = _normalize_post_url(link_tag["href"]) if link_tag else ""

                # Website (span or <a>)
                website = ""
                site_tag = row.select_one(".company-website")
                if site_tag:
                    website = site_tag.get_text(strip=True)

                # Description
                description = ""
                if "company-row-featured" in row.get("class", []):
                    description = featured_desc

                published = ""
                
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website=website,
                    published=str(published),
                    post_url=post_url,
                    country=""
                )

                """
                print('victim:', victim)
                print('post_url:', post_url)
                print('website:', website)
                print('description:', description)
                print('-' * 40)
                """

        except Exception as e:
            errlog(
                f"{group_name} - parsing fail with error: {e} in file: {filename}"
            )


if __name__ == "__main__":
    main()
