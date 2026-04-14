#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal parser for the LunaLock victims listing (HTML sample provided).
Matches your simple ransomware.live parser pattern (same imports, same appender signature).

What it extracts per card:
- victim: from <h2> title
- post_url: from the enclosing <a href="/victim/<slug>/">
- description: from the short <p> under the title (optional)
- website: "" (not present on listing)
- published: from the "Added <time datetime="YYYY-MM-DD">" (converted to "YYYY-MM-DD 00:00:00.000000")
- country: 2-letter code if present (e.g., "MX", "US")

Usage:
- Put the saved HTML into $RANSOMWARELIVE_HOME$TMP_DIR with filename starting with "lunalock-" (or symlink/filename determines group).
- Optional env BASE_URL to prefix absolute URLs if needed (e.g., http://onion).
"""

import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, find_slug_by_md5, extract_md5_from_filename

# --- config ---
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))
BASE_URL = os.getenv("BASE_URL", "")


def _group_name_from_self() -> str:
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        return os.path.basename(original_path).replace('.py','')
    return os.path.basename(script_path).replace('.py','')


def _normalize_post_url(href: str) -> str:
    if not href:
        return ""
    if BASE_URL and href.startswith('/'):
        return BASE_URL.rstrip('/') + href
    return href


def _parse_added_time(article) -> str:
    """Find the first <time datetime> inside the metadata row and format it."""
    try:
        t = article.find("time")
        if t and t.get("datetime"):
            iso = t.get("datetime").strip()
            # Incoming examples: YYYY-MM-DD
            if re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
                dt = datetime.datetime.fromisoformat(iso)
            else:
                # Fallback for full ISO forms
                iso = iso.replace("Z", "+00:00")
                dt = datetime.datetime.fromisoformat(iso)
            return dt.strftime("%Y-%m-%d 00:00:00.000000")
    except Exception:
        pass
    return ""


def _parse_country(article) -> str:
    # Last metadata span often contains a two-letter country code
    # Example markup: <span class="inline-flex ..."> MX </span>
    country = ""
    spans = article.select(".mt-2 span")
    for sp in spans[::-1]:  # search from the end
        txt = sp.get_text(" ", strip=True)
        m = re.search(r"\b([A-Z]{2})\b", txt)
        if m:
            country = m.group(1)
            break
    return country


def main():
    group_name = _group_name_from_self()

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + '-'):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # Cards are <article class="group ..."> inside a grid section
            cards = soup.select('section.grid article.group')
            for card in cards:
                a = card.find('a', href=True)
                post_url = _normalize_post_url(a['href']) if a else ''
                if post_url:
                    post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))).replace('victim/','')+ post_url

                title = card.find(['h2','h3'])
                victim = title.get_text(strip=True) if title else 'N/A'
                if "lunalock" in victim.lower():
                    continue

                p = card.find('p')
                description = p.get_text(' ', strip=True) if p else ''

                published = _parse_added_time(card)
                country = _parse_country(card)
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website="",
                    published=str(published),
                    post_url=post_url,
                    country=country
                )
                """
                print('victim:', victim)
                print('description:', description)
                print('published:', published)
                print('country:', country)
                print('post_url:', post_url)
                print('-'*40)
                """
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)


if __name__ == '__main__':
    main()
