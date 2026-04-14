#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re
from pathlib import Path
#from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
import pycountry
import tldextract
# ---------- Env ----------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# ---------- Helpers ----------
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)

def country_name_to_code(name: str) -> str:
    try:
        country = pycountry.countries.lookup((name or "").strip())
        return country.alpha_2.upper()
    except Exception:
        return ""


def text_clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip() if s else ""


def get_domain(url: str):
    if not url:
        return None
    try:
        ext = tldextract.extract(url)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}".lower()
        return None
    except Exception:
        return None

def safe_join_url(base: str, path: str) -> str:
    """Join base slug + relative link with exactly one slash."""
    base = (base or "").rstrip("/")
    path = (path or "").lstrip("/")
    return f"{base}/{path}" if base and path else (base or path)


def resolve_country(raw: str) -> str:
    """Convert country string (ISO2, full name, or 'City, Country') to ISO2."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    # Already ISO2
    if len(raw) == 2 and raw.isupper():
        return raw
    # "City, Country" → take the last part
    if "," in raw:
        raw = raw.split(",")[-1].strip()
    return country_name_to_code(raw)


def parse_card(card, base_slug: str, groupname: str):
    """Parse a single victim card and call appender."""
    name_tag = card.select_one("div.font-semibold")
    if not name_tag:
        return
    name = text_clean(name_tag.get_text())
    if not name:
        return

    lis = [text_clean(li.get_text()) for li in card.find_all("li")]

    website = get_domain(lis[0]) if len(lis) > 0 else ""
    country = resolve_country(lis[1]) if len(lis) > 1 else ""
    

    link_tag = card.select_one('a[href^="/company/"]')
    post_url = safe_join_url(base_slug, link_tag["href"]) if link_tag else ""




    appender(
        victim=name,
        group_name=groupname,
        description="",
        website=website or "",
        published="",
        post_url=post_url,
        country=country,
    )


def parse_file(path: Path, groupname: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.grid > div")
    if not cards:
        return

    md5 = extract_md5_from_filename(str(path))
    base_slug = find_slug_by_md5(groupname, md5)

    for card in cards:
        try:
            parse_card(card, base_slug, groupname)
        except Exception as e:
            errlog(f"{groupname} - card parse error: {e}")

def main():
    script_path = Path(os.path.abspath(__file__))
    if script_path.is_symlink():
        group_base = script_path.resolve().stem
    else:
        group_base = script_path.stem
    prefix = f"{group_base}-"

    candidates = sorted([
        p for p in tmp_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".html", ".htm"}
        and p.name.startswith(prefix)
    ])

    for p in candidates:
        if p.stat().st_size == 0:
            continue
        parse_file(p, group_base)

if __name__ == "__main__":
    main()
