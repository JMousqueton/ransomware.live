
import os
import datetime
import re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# Optional base URL (e.g., onion address) for building absolute links if needed
BASE_URL = os.getenv("BASE_URL", "").strip()  # e.g., http://shrantac...onion

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def to_micro_ts(date_str: str) -> str:
    """
    Convert a variety of date strings to 'YYYY-MM-DD HH:MM:SS.microseconds'.
    Returns '' if parsing fails.

    Supported:
      - ISO8601: '2026-01-05T12:34:56Z' or '2026-01-05T12:34:56+00:00'
      - Date-only: '16 Jan 2026' -> '2026-01-16 00:00:00.000000'
    """
    if not date_str:
        return ""
    s = date_str.strip()

    # ISO8601 first
    try:
        iso = s.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        pass

    # 'DD Mon YYYY'
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\b", s)
    if m:
        day, mon, year = m.groups()
        try:
            dt = datetime.datetime.strptime(f"{day} {mon} {year}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            return ""

    return ""

def strip_scheme(url: str) -> str:
    """Remove leading http:// or https:// (case-insensitive)."""
    if not url:
        return ""
    return re.sub(r"^https?://", "", url.strip(), flags=re.IGNORECASE)

def host_without_scheme(url: str) -> str:
    """
    Return only the hostname portion, without http(s)://.
    e.g., 'http://example.onion/path' -> 'example.onion'
    """
    if not url:
        return ""
    no_scheme = strip_scheme(url)
    return no_scheme.split("/", 1)[0] if "/" in no_scheme else no_scheme

def normalize_href(href: str) -> str:
    """
    If href is absolute, return as-is.
    If relative and BASE_URL is set, join them.
    Otherwise return 'N/A'.
    """
    if not href:
        return "N/A"
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if BASE_URL:
        base = BASE_URL.rstrip("/")
        if href.startswith("/"):
            return base + href
        else:
            return base + "/" + href
    return "N/A"

def extract_victim_from_card(a_tag) -> str:
    """
    In Black Shrantac list, the victim name is within:
      <div class="fw-semibold text-white">Victim Name</div>
    """
    name_div = a_tag.find("div", class_="fw-semibold")
    if name_div and name_div.get_text(strip=True):
        return name_div.get_text(strip=True)
    # Fallback: any strong-ish text in middle column
    middle = a_tag.find("div", class_="flex-grow-1")
    if middle:
        text = middle.get_text(" ", strip=True)
        if text:
            # Heuristic: first non-empty line before 'views'
            lines = [t.strip() for t in text.splitlines() if t.strip()]
            if lines:
                return lines[0]
    return "N/A"

def extract_views_from_card(a_tag) -> str:
    """
    Extracts numeric views from the 'text-secondary' div inside the card.
    Returns string like '36' or '' if not found.
    """
    sec = a_tag.find("div", class_="text-secondary")
    if not sec:
        # Sometimes class list may vary; fallback: search near the eye icon
        eye = a_tag.find("i", class_=lambda c: c and "fa-eye" in c)
        if eye and eye.parent:
            sec = eye.parent
    if sec:
        # Extract the first integer
        m = re.search(r"\b(\d+)\b", sec.get_text(" ", strip=True))
        if m:
            return m.group(1)
    return ""

def extract_date_from_card(a_tag) -> str:
    """
    The date is in a <div class="position-absolute" ...>YY Mon YYYY</div> block at the bottom-right.
    Returns formatted with microseconds or '' if not found.
    """
    # Find by class 'position-absolute'
    date_divs = a_tag.find_all("div", class_=lambda c: c and "position-absolute" in c)
    for d in date_divs:
        txt = d.get_text(strip=True)
        ts = to_micro_ts(txt)
        if ts:
            return ts
    # Fallback: try any small, grey text-like divs at end
    candidates = a_tag.find_all("div")
    for d in reversed(candidates):
        txt = d.get_text(strip=True)
        ts = to_micro_ts(txt)
        if ts:
            return ts
    return ""

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    # Derive group_name from real script path (handles symlinks)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    # Iterate over files in tmp_dir with naming convention: {group_name}-*
    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # The list lives under <nav class="sidebar"> ... ...
            sidebar = soup.find("nav", class_="sidebar")
            if not sidebar:
                continue

            items = sidebar.find_all("a", class_="sidebar-item")
            for a in items:
                # Victim name
                victim = extract_victim_from_card(a)

                # Post URL (detail page for the listing)
                href = a.get("href", "")
                post_url = normalize_href(href)

                # Published date (microseconds format)
                published = extract_date_from_card(a)  # '' if not present

                # Views (optional, placed into description)
                views = extract_views_from_card(a)

                # Website (actor site host without scheme). Prefer BASE_URL; fallback to host of post_url.
                website_host = host_without_scheme(BASE_URL) if BASE_URL else host_without_scheme(post_url)
                website = website_host  # already without http(s)://

                # Country: not present on this list page
                country = ""

                # Description: include views count if available
                desc_parts = []
                if views:
                    desc_parts.append(f"Views: {views}")
                description = " | ".join(desc_parts) if desc_parts else ""

                # Append record
                '''
                print('victim:',victim)
                print('post_url:',post_url)
                print('published:',published)
                print('website:',website)
                print('description:',description)
                print('-'*40)
                '''
                appender(
                    victim=victim,
                    group_name=group_name,
                    description='',
                    website='',
                    published=str(published),  # 'YYYY-MM-DD HH:MM:SS.%f' or ''
                    post_url=post_url,
                    country=''
                )
             
        except Exception as e:
            errlog(group_name + " - parsing fail with error: " + str(e) + " in file: " + filename)

if __name__ == "__main__":
    main()
