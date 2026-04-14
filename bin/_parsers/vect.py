
import os
import datetime
import sys
import re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

# Load environment (.env at ../.env)
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# Optional base URL (e.g., onion address) to populate post_url when the page lacks per-victim links
BASE_URL = os.getenv("BASE_URL", "").strip()  # e.g., http://xxxx.onion

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def to_micro_ts(date_str: str) -> str:
    """
    Convert various date strings to 'YYYY-MM-DD HH:MM:SS.microseconds'.
    Returns '' if parsing fails.

    Supported inputs:
      - ISO8601: '2026-01-05T12:34:56Z' or '2026-01-05T12:34:56+00:00'
      - Date-only: '05 Jan 2026' -> '2026-01-05 00:00:00.000000'
    """
    if not date_str:
        return ""
    s = date_str.strip()

    # Try ISO8601 first (normalize trailing 'Z' to timezone)
    try:
        iso = s.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        pass

    # Try "DD Mon YYYY" (English short month), default to midnight if no time info
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\b", s)
    if m:
        day, mon, year = m.groups()
        try:
            dt = datetime.datetime.strptime(f"{day} {mon} {year}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            return ""

    return ""


def normalize_site(site: str) -> str:
    """
    Normalize SITE value by removing 'http://' or 'https://'.
    If it's a bare domain like 'hytec.com', keep it as-is.
    """
    if not site:
        return ""
    site = site.strip()

    # Remove protocol if present
    site = re.sub(r"^https?://", "", site, flags=re.IGNORECASE)

    return site


def extract_card_meta(meta_text: str) -> dict:
    """
    Parse 'SECTOR', 'COUNTRY', 'SITE' from the card-meta line which uses bullets '•'.
    Example:
      'SECTOR: Engineering Solutions • COUNTRY: SA • SITE: hytec.com'
    """
    res = {"sector": "", "country": "", "site": ""}
    if not meta_text:
        return res

    # Collapse whitespace for robust matching
    text = " ".join(meta_text.split())

    # Extract segments using regex; stop at bullet or end-of-line
    sector_m = re.search(r"SECTOR:\s*(.*?)(?:\s*•|$)", text, flags=re.IGNORECASE)
    country_m = re.search(r"COUNTRY:\s*(.*?)(?:\s*•|$)", text, flags=re.IGNORECASE)
    site_m = re.search(r"SITE:\s*(.*?)(?:\s*•|$)", text, flags=re.IGNORECASE)

    if sector_m:
        res["sector"] = sector_m.group(1).strip()
    if country_m:
        res["country"] = country_m.group(1).strip()
    if site_m:
        res["site"] = site_m.group(1).strip()
    return res

def extract_date_info(date_text: str) -> tuple[str, str]:
    """
    Extract publication date and deadline from the 'date-info' line.
    Returns (published_str, deadline_str) where published_str is formatted
    as 'YYYY-MM-DD HH:MM:SS.%f' (microseconds). If parsing fails, published_str = ''.

    Example input:
      "ENTRY 01 | 05 Jan 2026 | DEADLINE: 4d 15h"
    """
    if not date_text:
        return ("", "")

    # Extract the date part like '05 Jan 2026'
    date_m = re.search(r"\b(\d{1,2}\s+\w{3}\s+\d{4})\b", date_text)
    deadline_m = re.search(r"DEADLINE:\s*([^\|]+)", date_text, flags=re.IGNORECASE)

    published_str = ""
    if date_m:
        raw = date_m.group(1).strip()
        published_str = to_micro_ts(raw)  # midnight if time not present

    deadline_str = deadline_m.group(1).strip() if deadline_m else ""
    return (published_str, deadline_str)

def extract_victim(card) -> str:
    """
    Prefer <h2> (proper case) as victim name; fallback to <h3> or '.sealed-stamp'.
    """
    h2 = card.find("h2")
    if h2 and h2.get_text(strip=True):
        return h2.get_text(strip=True)

    h3 = card.find("h3")
    if h3 and h3.get_text(strip=True):
        return h3.get_text(strip=True)

    stamp = card.find("div", class_="sealed-stamp")
    if stamp and stamp.get_text(strip=True):
        return stamp.get_text(strip=True)

    return "N/A"

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    # Derive group_name from this script's real path (handling symlinks)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    # Iterate over files in tmp_dir with the naming convention: {group_name}-*
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename

                # Read HTML as UTF-8
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                # All victims are in <main class="victim-grid"> with <div class="victim-card">
                victim_cards = soup.find_all("div", class_="victim-card")
                for card in victim_cards:
                    # --- Victim ---
                    victim = extract_victim(card)

                    # --- Date & Deadline ---
                    date_info = card.find("p", class_="date-info")
                    date_text = date_info.get_text(" ", strip=True) if date_info else ""
                    published, deadline = extract_date_info(date_text)

                    # --- Status ---
                    status_tag = card.find("p", class_="status-tag")
                    status_text = status_tag.get_text(" ", strip=True) if status_tag else ""

                    # --- Card Meta (Sector, Country, Site) ---
                    meta = card.find("p", class_="card-meta")
                    meta_text = meta.get_text(" ", strip=True) if meta else ""
                    meta_vals = extract_card_meta(meta_text)
                    sector = meta_vals.get("sector", "")
                    country = meta_vals.get("country", "")
                    site_raw = meta_vals.get("site", "")
                    website = normalize_site(site_raw)

                    # --- Body description ---
                    body_paragraphs = []
                    card_body = card.find("div", class_="card-body")
                    if card_body:
                        for p in card_body.find_all("p"):
                            # Exclude date-info and card-meta already handled
                            if "date-info" in p.get("class", []) or "card-meta" in p.get("class", []):
                                continue
                            body_paragraphs.append(p.get_text(" ", strip=True))

                    # Build description string
                    desc_parts = []
                    if status_text:
                        desc_parts.append(f"Status: {status_text}")
                    if sector:
                        desc_parts.append(f"Sector: {sector}")
                    if body_paragraphs:
                        desc_parts.append(" ".join(body_paragraphs))
                    if deadline:
                        desc_parts.append(f"Deadline: {deadline}")

                    description = " | ".join([part for part in desc_parts if part])

                    # --- Post URL ---
                    # The sample HTML doesn't provide per-victim post links; use BASE_URL if available.
                    post_url = BASE_URL if BASE_URL else "N/A"

                    # Append the record
                    
                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        published=str(published),   # already microsecond-format or ''
                        post_url="",
                        country=country
                    )
                    """
                    print('Victim:', victim)
                    print('Group Name:', group_name)
                    print('Description:', description)
                    print('Website:', website)  
                    print('Published:', str(published))
                    print('Post URL:', post_url)
                    print('Country:', country)
                    print('---')
                    """
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

if __name__ == "__main__":
    main()
