#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, find_slug_by_md5, extract_md5_from_filename, stdlog
from urllib.parse import urlparse

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME", "")
tmp_dir = Path(home + os.getenv("TMP_DIR", "./tmp"))

URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)

def first_url(text: str) -> str:
    if not text:
        return ""
    m = URL_RE.search(text)
    return m.group(0) if m else ""

def normalize_desc(node) -> str:
    if node is None:
        return ""
    for br in node.find_all("br"):
        br.replace_with("\n")
    txt = node.get_text(separator=" ", strip=True)
    txt = re.sub(r"[ \t]*\n[ \t]*", "\n", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt).strip()
    return txt

def main():
    # Resolve group name from symlink or filename
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + "-"):
            continue

        try:
            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as file:
                soup = BeautifulSoup(file, "html.parser")

            cards = soup.find_all("div", class_="b_block")
            if not cards:
                errlog(group_name + f" - no .b_block found in {filename}")
                continue
            url = find_slug_by_md5('alphalocker', extract_md5_from_filename(str(html_doc)))
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}/"

            for card in cards:
                try:
                    title_a = card.select_one(".news_title a.a_title")
                    if not title_a:
                        errlog(group_name + f" - missing .news_title a.a_title in {filename}")
                        continue

                    victim = title_a.get_text(" ", strip=True)
                    post_url = base_url + (title_a.get("href") or "").strip()
                    website = first_url(victim)
                    website_parsed = urlparse(website)
                    website = website_parsed.netloc

                    news_div = card.select_one(".news_div")
                    desc_block = None
                    if news_div:
                        for div in news_div.find_all("div", recursive=False):
                            style = div.get("style", "")
                            if "line-height" in style and "20px" in style:
                                desc_block = div
                                break
                        if not desc_block:
                            title_div = news_div.select_one(".news_title")
                            if title_div:
                                sib = title_div.find_next_sibling("div")
                                if sib:
                                    desc_block = sib

                    description = normalize_desc(desc_block)
                    victim = re.sub(r"https?://", "", victim)
                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        post_url=post_url,
                    )
                    """
                    print('victim:', victim)
                    print('description:', description)
                    print('website:', website)
                    print('post_url:', post_url)
                    print('-'*40)
                    """    
                except Exception as ie:
                    errlog(group_name + f" - card parse error: {ie} in file: {filename}")
                    continue

        except Exception as e:
            errlog(group_name + " - parsing fail with error: " + str(e) + " in file: " + filename)

if __name__ == "__main__":
    main()
