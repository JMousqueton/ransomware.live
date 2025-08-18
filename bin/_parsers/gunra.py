#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
import pycountry
# ---------- Env ----------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# ---------- Helpers ----------
TB_GB_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(T|G)B?\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)

def country_name_to_code(name: str) -> str:
    try:
        country = pycountry.countries.lookup((name or "").strip())
        return country.alpha_2.upper()
    except Exception:
        return ""


def text_clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip() if s else ""

def split_name_size(title_text: str):
    t = text_clean(title_text)
    parts = [p.strip() for p in t.split("|")]
    if len(parts) > 1:
        m = TB_GB_RE.search(parts[-1])
        if m:
            size_val, unit = m.groups()
            unit = unit.upper()
            if unit == "T":
                unit = "TB"
            elif unit == "G":
                unit = "GB"
            size = f"{size_val}{unit}"
            name = " | ".join(parts[:-1]).strip()
            return name, size
    m = TB_GB_RE.search(t)
    if m:
        size_val, unit = m.groups()
        unit = unit.upper()
        if unit == "T":
            unit = "TB"
        elif unit == "G":
            unit = "GB"
        size = f"{size_val}{unit}"
        name = t[:m.start()].rstrip(" |")
        return text_clean(name), size
    return t, None

def get_domain(url: str):
    if not url:
        return None
    try:
        p = urlparse(url)
        return p.netloc or None
    except Exception:
        return None

def find_info_div(anchor):
    steps = 0
    for el in anchor.next_elements:
        if steps > 800:
            break
        steps += 1
        if getattr(el, "name", None) == "div":
            txt = el.get_text(" ", strip=True)
            if "industry:" in txt.lower() or "location:" in txt.lower():
                return el
        if getattr(el, "name", None) == "strong":
            break

    parent = anchor.parent
    for _ in range(4):
        if not parent or not getattr(parent, "find_all", None):
            break
        for d in parent.find_all("div"):
            txt = d.get_text(" ", strip=True).lower()
            if "industry:" in txt or "location:" in txt:
                return d
        parent = parent.parent
    return None

def parse_item(anchor):
    link = anchor.get("href")
    name, size = split_name_size(anchor.get_text(" ", strip=True))

    industry = location = domain = None
    info_div = find_info_div(anchor)
    if info_div:
        line = text_clean(info_div.get_text(" ", strip=True))
        for seg in [p.strip() for p in line.split("|")]:
            sl = seg.lower()
            if sl.startswith("industry:"):
                industry = text_clean(seg.split(":", 1)[1])
            elif sl.startswith("location:"):
                location = text_clean(seg.split(":", 1)[1])
        a = info_div.find("a")
        if a and a.has_attr("href"):
            domain = get_domain(a["href"])
        if not domain:
            m = URL_RE.search(info_div.get_text(" ", strip=True))
            if m:
                domain = get_domain(m.group(0))

    return name, size, industry, location, domain, link

def safe_join_url(base: str, path: str) -> str:
    """Join base slug + relative link with exactly one slash."""
    base = (base or "").rstrip("/")
    path = (path or "").lstrip("/")
    return f"{base}/{path}" if base and path else (base or path)


def parse_file(path: Path, groupname: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    for parser in ("lxml", "html.parser"):
        soup = BeautifulSoup(html, parser)
        anchors = soup.select("strong > a")
        if not anchors:
            anchors = []
            for a in soup.select("a[href]"):
                if not a.get_text(strip=True):
                    continue
                if find_info_div(a):
                    anchors.append(a)
        if anchors:
            # compute base slug once per file
            md5 = extract_md5_from_filename(str(path))
            base_slug = find_slug_by_md5(groupname, md5)
            for a in anchors:
                name, size, industry, location, domain, link = parse_item(a)
                if not name:
                    continue
                extra_infos = {
                    "Activity": industry or "",
                    "data_size": size or ""
                }
                post_url = safe_join_url(base_slug, link or "")
                country = country_name_to_code(location) if location else ""
                appender(
                    victim=name,
                    group_name=groupname,
                    description="",
                    website=domain or "",
                    published="",       
                    post_url=post_url,
                    country=country,
                    extra_infos=extra_infos
                )
            return

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
