#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from datetime import datetime
import pycountry
from rapidfuzz import process, fuzz
from urllib.parse import urlparse

# ----- ENV -----
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME") or ""
tmp_dir = Path(home + (os.getenv("TMP_DIR") or ""))

# ----- Helpers -----
WS_RE = re.compile(r"\s+")
def normspace(s: str) -> str:
    return WS_RE.sub(" ", s or "").strip()

def only_domain(s: str) -> str:
    v = (s or "").strip()
    if re.match(r"^https?://", v, flags=re.I):
        return urlparse(v).netloc.lower()
    return v.lower()

def convert_date(date_str: str) -> str:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", date_str or "")
    if not m:
        # fallback for mm/dd/yy if they ever use it
        try:
            return datetime.strptime(date_str, "%m/%d/%y").strftime("%Y-%m-%d 00:00:00.000000")
        except Exception:
            return ""
    mm, dd, yyyy = map(int, m.groups())
    return f"{yyyy:04d}-{mm:02d}-{dd:02d} 00:00:00.000000"

def get_country_code(location):
    if not location:
        return ""
    location = location.replace("📍", "").strip()
    if len(location) == 2:
        c = pycountry.countries.get(alpha_2=location.upper())
        if c: return c.alpha_2
    if len(location) == 3:
        c = pycountry.countries.get(alpha_3=location.upper())
        if c: return c.alpha_2
    try:
        c = pycountry.countries.search_fuzzy(location)
        if c: return c[0].alpha_2
    except LookupError:
        all_names = [c.name for c in pycountry.countries]
        best = process.extractOne(location, all_names, scorer=fuzz.ratio)
        if best and best[1] > 80:
            m = pycountry.countries.get(name=best[0])
            if m: return m.alpha_2
    return ""

def parse_card(card, group_name, html_doc):
    """Extract one victim from a 900px table card."""
    left_td = card.select_one("td[style*='width:670px']")
    if not left_td:
        return None

    # Title line: <p><strong>Victim [flag]</strong> <mark>STATUS</mark></p>
    p_list = left_td.find_all("p")
    if not p_list:
        return None
    title_p = p_list[0]
    strong = title_p.find("strong")
    if not strong:
        return None
    for sp in strong.find_all("span"):
        sp.extract()
    victim_name = normspace(strong.get_text())

    status = ""
    mark = title_p.find("mark")
    if mark:
        status = normspace(mark.get_text()).lower()

    description = ""
    if len(p_list) >= 2:
        description = normspace(p_list[1].get_text())

    # Collapsible info
    info = left_td.select_one(".info__body")
    published = website = industry = location = revenue = details_path = ""

    if info:
        # Iterate explicit <p> lines for label:value
        for p in info.find_all("p"):
            line = p.get_text(" ", strip=True)
            low = line.lower()
            if low.startswith("date company notified:"):
                published = convert_date(line.split(":", 1)[1].strip())
            elif low.startswith("site:"):
                a = p.find("a", href=True)
                if a:
                    website = only_domain(a.get_text(strip=True) or a["href"])
                else:
                    website = only_domain(line.split(":", 1)[1].strip())
            elif low.startswith("industry:"):
                industry = line.split(":", 1)[1].strip()
            elif low.startswith("location:"):
                location = line.split(":", 1)[1].replace("📍", "").strip()
            elif low.startswith("revenue:"):
                revenue = line.split(":", 1)[1].strip()
            elif p.find("a", href=True) and "details" in low:
                details_path = p.find("a")["href"]

    # Build post_url with your slug/md5
    post_url = ""
    if details_path:
        md5 = extract_md5_from_filename(str(html_doc))
        slug = find_slug_by_md5(group_name, md5)
        post_url = f"{slug}/{details_path}"

    country = get_country_code(location)

    return {
        "victim": victim_name,
        "group_name": group_name,
        "description": description,
        "website": website,
        "published": published,
        "post_url": post_url,
        "country": country,
        "extra_infos": {
            "Activity": industry,
            "Revenue": revenue,
            "Status": status  # keep if you want to see ANNOUNCED / SAMPLES POSTED
        },
    }

def main():
    # Resolve group name from filename (handles symlinks)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        origin = os.readlink(script_path)
        if not os.path.isabs(origin):
            origin = os.path.join(os.path.dirname(script_path), origin)
        group_name = os.path.basename(origin).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    try:
        files = sorted([f for f in os.listdir(tmp_dir) if f.startswith(group_name + "-")])
    except Exception as e:
        errlog(f"{group_name} - cannot list tmp_dir '{tmp_dir}': {e}")
        return

    for filename in files:
        html_doc = tmp_dir / filename
        try:
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as fh:
                soup = BeautifulSoup(fh, "html.parser")
        except Exception as e:
            errlog(f"{group_name} - read error: {e} in file: {filename}")
            continue

        try:
            # Each victim block is a 900px table with a .info__body section
            cards = soup.select("table[style*='width:900px']")
            for card in cards:
                if not card.select_one(".info__body"):
                    continue
                rec = parse_card(card, group_name, html_doc)
                if not rec:
                    continue

                appender(
                    victim=rec["victim"],
                    group_name=rec["group_name"],
                    description=rec["description"],
                    website=rec["website"],
                    published=rec["published"],
                    post_url=rec["post_url"],
                    country=rec["country"],
                    extra_infos=rec["extra_infos"],
                )
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")

if __name__ == "__main__":
    main()
