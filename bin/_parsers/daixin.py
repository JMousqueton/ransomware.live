#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog
from urllib.parse import urlparse
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# ---------- helpers ----------
SPACE_RE = re.compile(r"\s+")
PAREN_RE = re.compile(r"\(([^)]+)\)")
SPLIT_COUNTRY_RE = re.compile(r"[,;/]|\band\b", flags=re.I)

def normspace(s: str) -> str:
    return SPACE_RE.sub(" ", (s or "").strip())

def clean_title(h4) -> str:
    if not h4:
        return ""
    for img in h4.find_all("img"):
        img.decompose()
    return normspace(h4.get_text(" ", strip=True))

def alpha3_to_alpha2(code: str) -> str:
    """Convert ISO-3166 alpha-3 to alpha-2 if possible."""
    try:
        return pycountry.countries.get(alpha_3=code).alpha_2
    except Exception:
        return code  # fallback if not found

def extract_1st_country(title: str) -> str:
    if not title:
        return ""
    m = PAREN_RE.search(title)
    if not m:
        return ""
    inside = normspace(m.group(1))
    first_token = SPLIT_COUNTRY_RE.split(inside)[0].strip()
    m_iso = re.search(r"\b([A-Z]{2,3})\b", first_token)
    if m_iso:
        code = m_iso.group(1)
        if len(code) == 3:   # Convert 3-letter to 2-letter
            return alpha3_to_alpha2(code)
        return code
    return first_token

def strip_country_from_title(title: str) -> str:
    if not title:
        return ""
    return normspace(re.sub(r"\s*\([^)]*\)\s*$", "", title))

def get_website(card) -> str:
    for h6 in card.find_all("h6"):
        txt = h6.get_text(" ", strip=True).lower()
        if "web site" in txt:
            a = h6.find("a", href=True)
            if a and a.get("href"):
                href = a["href"].strip()
                # Normalize to include scheme if missing
                if not re.match(r"^https?://", href, flags=re.I):
                    href = "https://" + href.lstrip()
                try:
                    return re.sub(r"^www\.", "", urlparse(href).netloc.lower())
                except Exception:
                    return ""
    return ""


def get_description_before_hr(card) -> str:
    desc_parts = []
    for child in card.children:
        name = getattr(child, "name", None)
        if name == "hr":
            break
        if name == "p":
            cls = child.get("class") or []
            if "card-text" in cls:
                t = normspace(child.get_text(" ", strip=True))
                if t:
                    desc_parts.append(t)
    return normspace(" ".join(desc_parts))

# ---------- main ----------
def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + '-'):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                cards = soup.find_all("div", class_="card-body")
                for card in cards:
                    try:
                        h4 = card.find("h4")
                        raw_title = clean_title(h4)
                        if not raw_title:
                            continue

                        country = extract_1st_country(raw_title)
                        victim = strip_country_from_title(raw_title)

                        website = get_website(card)
                        description = get_description_before_hr(card)

                        
                        if not description:
                            continue
                        
                        appender(
                            victim=victim,
                            group_name=group_name,
                            description=description,
                            website=website,
                            published="",
                            post_url="",
                            country=country
                        )

                    except Exception as e_card:
                        errlog(group_name + ' - card parse error: ' + str(e_card) + ' in file: ' + filename)

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

if __name__ == "__main__":
    main()
