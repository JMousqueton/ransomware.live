#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, datetime, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def normalize_published(_: str) -> str:
    """
    MS13-089 pages do not expose a publication date.
    Keep empty string to stay schema-compatible.
    """
    return ""


def extract_post_url(el) -> str:
    """
    Extract URL from onclick="location.href='...'"
    """
    if not el:
        return ""
    onclick = el.get("onclick", "")
    m = re.search(r"location\.href=['\"]([^'\"]+)['\"]", onclick)
    return m.group(1) if m else ""

def extract_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def extract_domain(text: str) -> str:
    """
    Extract first domain only
    Example: 'uro.com (USA, Virginia)' -> 'uro.com'
    """
    if not text:
        return ""
    m = re.search(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", text)
    return m.group(0) if m else ""


def main():
    # Determine group_name from script name or symlink
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")


    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

                # Each victim card
                posts = soup.select("div.post.bad")
                for post in posts:
                    title_el = post.select_one(".post-title-block > div")
                    desc_el = post.select_one(".post-text")

                    title_text = extract_text(title_el)
                    description = extract_text(desc_el)

                    website = extract_domain(title_text)
                    victim = website or title_text or "N/A"

                    published = normalize_published("")
                    more_el = post.select_one("a.post-more-link")
                    post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))  + extract_post_url(more_el)
                    post_url = post_url.replace("cl/clicks.php?uri=","")
                    country = ""

                    # Optional: extract country if you want later
                    # e.g. uro.com (USA, Virginia)
                    # match = re.search(r"\(([^)]+)\)", title_text)
                    # country = match.group(1) if match else ""
                    
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
                    print('victim:', victim)
                    print('description:', description)
                    print('website:', website)
                    print('published:', published)
                    print('post_url:', post_url)
                    print('country:', country)
                    print('---')
                    """
        except Exception as e:
            errlog(
                f"{group_name} - parsing fail with error: {e} in file: {filename}"
            )


if __name__ == "__main__":
    main()
