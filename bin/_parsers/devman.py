import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, extract_md5_from_filename, find_slug_by_md5
import pycountry
from rapidfuzz import process, fuzz
from datetime import datetime

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def safe_text(el):
    return el.get_text(strip=True) if el else ""

def normalize_pubdate(value: str) -> str:
    """
    Convert DEVMAN dates like 'Dec 06, 2025' into:
    '2025-12-06 00:00:00.000000'
    """
    if not value:
        return ""

    value = value.strip()

    try:
        dt = datetime.strptime(value, "%b %d, %Y")
        # zero time, microseconds included
        return dt.strftime("%Y-%m-%d 00:00:00.000000")
    except:
        return ""


def country_to_iso2(value: str) -> str:
    """
    Normalize country names using pycountry.
    Handles:
    - ISO2
    - ISO3
    - Full names
    - Common abbreviations
    - Typos (via fuzzy matching)
    """
    if not value:
        return ""

    v = value.strip()

    # Already ISO2?
    if len(v) == 2 and v.isalpha():
        return v.upper()

    u = v.upper()

    # Common shortcuts
    COMMON = {
        "USA": "US",
        "U.S.A": "US",
        "UNITED STATES": "US",
        "UK": "GB",
        "UAE": "AE",
        "ISRL": "IL",   # DEVMAN
        "JRD": "JO",    # DEVMAN
        "PHILIPINES": "PH",
        "PHILIPPINES": "PH",
    }
    if u in COMMON:
        return COMMON[u]

    # Try ISO3
    try:
        c = pycountry.countries.get(alpha_3=u)
        if c:
            return c.alpha_2
    except:
        pass

    # Try name match
    try:
        c = pycountry.countries.search_fuzzy(v)
        if c:
            return c[0].alpha_2
    except:
        pass

    # Try fuzzy match with all country names
    names = [c.name for c in pycountry.countries]
    best, score, idx = process.extractOne(v, names, scorer=fuzz.WRatio)

    if score > 85:  # good confidence
        return pycountry.countries.lookup(best).alpha_2

    return ""

def parse_data_grid(block):
    data = {}
    if not block:
        return data
    for f in block.find_all("div", class_="data-field"):
        label = safe_text(f.find("div", class_="field-label"))
        value = safe_text(f.find("div", class_="field-value"))
        if label and value:
            data[label] = value
    return data


def resolve_post_url(group_name, html_doc):
    """Resolve the ransomware.live canonical link by MD5 → slug lookup."""
    md5 = extract_md5_from_filename(str(html_doc))
    if not md5:
        return ""

    try:
        slug = find_slug_by_md5(group_name, md5)
        if slug:
            return slug
    except Exception as e:
        errlog(f"[{group_name}] slug lookup failed for {md5}: {e}")

    return ""


def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + "-"):
            continue

        html_doc = tmp_dir / filename

        try:
            with open(html_doc, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

            leak_items = soup.find_all("div", class_="leak-item")
            if not leak_items:
                errlog(f"[{group_name}] No leak-item found in {filename}")
                continue

            post_url = resolve_post_url(group_name, html_doc)

            for item in leak_items:
                header = item.find("div", class_="leak-header")

                company = safe_text(header.find("div", class_="leak-company"))

                info = header.find("div", class_="leak-info")
                spans = [safe_text(s) for s in info.find_all("span")] if info else []

                category = spans[0] if len(spans) > 0 else ""
                raw_country = spans[1] if len(spans) > 1 else ""
                country = country_to_iso2(raw_country)
                raw_published = spans[2] if len(spans) > 2 else ""
                published = normalize_pubdate(raw_published)

                body = item.find("div", class_="leak-body")

                desc = safe_text(body.find("div", class_="leak-desc")) if body else ""

                datagrid = body.find("div", class_="data-grid") if body else None
                datadict = parse_data_grid(datagrid)

                website = datadict.get("Website", "")

                # -----------------------------------------------------------
                # NEW APPENDER FORMAT
                # -----------------------------------------------------------
                
                appender(
                    victim=company,
                    group_name=group_name,
                    description=desc,
                    website=website,
                    published=str(published),
                    post_url=post_url,
                    country=country
                )
                """
                print('Victim:',company)
                print('Desc.:',desc)
                print('web:',website)
                print('pub:',str(published))
                print('post:',post_url)
                print('country:',country)
                print('*'*40)
                """
        except Exception as e:
            errlog(f"[{group_name}] Error in {filename}: {e}")


if __name__ == "__main__":
    main()
