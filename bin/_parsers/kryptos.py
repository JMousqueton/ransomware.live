#!/usr/bin/env python3
# kryptos.py — parser for Kryptos leaks and Magi-kard style entries

import os, sys, datetime, re
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from shared_utils import appender, errlog

# pip install pycountry
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def text(el):
    return el.get_text(strip=True) if el else ""

def iso_datetime(s):
    """Convert '2025-10-19T17:00:00Z' or 'dd-mm-yyyy' into 'YYYY-MM-DD HH:MM:SS.000000'."""
    if not s:
        return ""
    try:
        if s.endswith("Z"):
            dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.datetime.fromisoformat(s)
        return dt.strftime("%Y-%m-%d %H:%M:%S.000000")
    except Exception:
        m = re.match(r"^\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*$", s)
        if m:
            d, mo, y = m.groups()
            y = y if len(y) == 4 else ("20" + y)
            try:
                dt = datetime.datetime(int(y), int(mo), int(d), 0, 0, 0, 0)
                return dt.strftime("%Y-%m-%d 00:00:00.000000")
            except Exception:
                return ""
        return ""

def normalize_country_name(name):
    """Light normalization + a few common aliases before pycountry lookup."""
    if not name:
        return ""
    s = name.strip()
    # if input is "City, Country", keep only the last segment
    if "," in s:
        s = s.split(",")[-1].strip()
    # common aliases & abbreviations
    aliases = {
        "UK": "United Kingdom",
        "U.K.": "United Kingdom",
        "USA": "United States",
        "U.S.A.": "United States",
        "United States of America": "United States",
        "South Korea": "Korea, Republic of",
        "North Korea": "Korea, Democratic People's Republic of",
        "Russia": "Russian Federation",
        "UAE": "United Arab Emirates",
        "Cote d'Ivoire": "Côte d'Ivoire",
    }
    s = s.replace("’", "'").replace("′", "'").strip(". ")
    s = aliases.get(s, s)
    # Some pages say "International" or multiple countries -> return empty
    if s.lower() in {"international", "global", "multiple", "worldwide", "n/a"}:
        return ""
    return s

def country_to_alpha2(country_str):
    """Return ISO 3166-1 alpha-2 (e.g., 'FR') from a raw string like 'Paris, France'."""
    name = normalize_country_name(country_str)
    if not name:
        return ""
    try:
        country = pycountry.countries.lookup(name)
        return country.alpha_2
    except Exception:
        return ""

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
            with open(html_doc, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')

            # --- Case 1: .Magi-kard cards ---
            for card in soup.select(".Magi-kard"):
                try:
                    victim = text(card.select_one(".vting-name")) or "N/A"
                    victim = victim.replace("█", "*")

                    # post URL detection
                    post_url = ""
                    onclick = card.get("onclick") or ""
                    m_href = re.search(r"window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]", onclick)
                    if m_href:
                        post_url = m_href.group(1).strip()
                    else:
                        m_nav = re.search(r"navigateToVtin\(['\"]([^'\"]+)['\"]\)", onclick)
                        if m_nav:
                            post_url = f"/vtin/{m_nav.group(1).strip()}"
                        else:
                            a = card.find("a", href=True)
                            if a:
                                post_url = a["href"].strip()

                    # Collect simple fields from .data-item / .meta-item
                    fields = {}
                    for di in card.select(".data-item"):
                        lab = text(di.select_one(".data-label")).strip(": ").lower()
                        val = text(di.select_one(".data-value"))
                        if lab:
                            key = re.sub(r"\W+", "_", lab).strip("_")
                            fields[key] = val

                    for mi in card.select(".meta-item"):
                        lab = text(mi.select_one(".meta-label")).strip(": ").lower()
                        val = text(mi.select_one(".meta-value"))
                        if lab:
                            key = re.sub(r"\W+", "_", lab).strip("_")
                            fields[key] = val

                    published = iso_datetime(fields.get("breach_date", ""))

                    # Try to convert countries_data_incl (may be 'City, Country' or just 'Country')
                    raw_country = fields.get("countries_data_incl", "") or fields.get("country", "")
                    country = country_to_alpha2(raw_country)

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description="",
                        website="",
                        published=str(published),
                        post_url=post_url,
                        country=country
                    )
                except Exception as e:
                    errlog(f"{group_name} - Magi-kard parse error: {e} in file: {filename}")

            # --- Case 2: .leak blocks ---
            for leak in soup.select(".leak"):
                try:
                    timer = leak.select_one(".timer")
                    published = iso_datetime(timer.get("data-date")) if timer else ""

                    locked = leak.select_one(".locked")
                    victim = ""
                    country = ""
                    website = ""
                    description = ""

                    if locked:
                        victim = text(locked.find("strong")) or "N/A"
                        victim = victim.replace("█", "*")

                        em = locked.find("em")
                        if em:
                            parts = [p.strip() for p in em.get_text(" ").split("·") if p.strip()]
                            # heuristic: industry · location · employees
                            # parts[1] likely "City, Country" or "Country"
                            loc_text = parts[1] if len(parts) >= 2 else ""
                            country = country_to_alpha2(loc_text)

                            # build a short description (industry; employees)
                            description = "; ".join([
                                parts[0] if len(parts) >= 1 else "",
                                parts[2] if len(parts) >= 3 else ""
                            ]).strip("; ").strip()

                        code = locked.find("code")
                        if code:
                            website = text(code)
                            if "█" in website:
                                website = ""

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        published="",
                        post_url="",
                        country=country
                    )
                except Exception as e:
                    errlog(f"{group_name} - leak block parse error: {e} in file: {filename}")

        except Exception as e:
            try:
                errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
            except Exception:
                sys.stderr.write(f"{group_name} - parsing fail: {e} in file: {filename}\n")

if __name__ == "__main__":
    main()
