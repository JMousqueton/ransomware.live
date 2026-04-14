
import os
import datetime
import re
from urllib.parse import urlparse, urljoin
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

# Optional base URL (e.g., onion address) for building absolute links
# Example: BASE_URL=http://toolatedhs5dtr2pv6h5kdraneak5gs3sxrecqhoufc5e45edior7mqd.onion/
BASE_URL = os.getenv("BASE_URL", "").strip()

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def to_micro_ts(date_str: str) -> str:
    """
    Convert a variety of date strings to 'YYYY-MM-DD HH:MM:SS.microseconds'.
    Returns '' if parsing fails.

    Supported:
      - ISO8601: '2025-09-28T13:40:00Z' or '2025-09-28T13:40:00+00:00'
      - Date-only: '23 Jan 2026' -> '2026-01-23 00:00:00.000000'
    """
    if not date_str:
        return ""
    s = date_str.strip()

    # ISO8601 first (normalize trailing 'Z' to timezone)
    try:
        iso = s.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        pass

    # 'DD Mon YYYY' (English)
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
    # If already scheme-less host/path, split yourself
    if "://" not in url:
        return url.split("/", 1)[0]
    parts = urlparse(url)
    return parts.netloc

def normalize_href(href: str, base_url: str = "", fallback_host: str = "") -> str:
    """
    Normalize relative/absolute HREF to absolute URL.
    Priority:
      1) If href is absolute -> return as-is
      2) If base_url present -> urljoin(base_url, href)
      3) If fallback_host present -> urljoin('http://{host}/', href)
      4) Otherwise -> 'N/A'
    """
    if not href:
        return "N/A"
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if base_url:
        base = base_url.rstrip("/") + "/"
        return urljoin(base, href)
    if fallback_host:
        base = f"http://{fallback_host.strip('/')}/"
        return urljoin(base, href)
    return "N/A"

def get_hidden_service_host(soup: BeautifulSoup) -> str:
    """
    Try to discover the Hidden Service host from the "Hidden Service" tab link,
    e.g., <a class="tab-btn" href="http://toolated....onion/" ...>Hidden Service</a>
    Returns the hostname without scheme (or '' if not found).
    """
    for a in soup.select('nav.tabs a.tab-btn'):
        text = a.get_text(" ", strip=True).lower()
        if "hidden service" in text and a.get("href"):
            return host_without_scheme(a["href"])
    return ""

def extract_victim(article: BeautifulSoup) -> str:
    """Victim name from <h3> inside the .front section."""
    h3 = article.select_one("section.front h3")
    return h3.get_text(strip=True) if h3 else "N/A"

def extract_description_text(front_section: BeautifulSoup) -> str:
    """Extract the main breach description from the <p> inside .front."""
    p = front_section.select_one("p")
    return p.get_text(" ", strip=True) if p else ""

def extract_deadline(front_section: BeautifulSoup) -> str:
    """Extract deadline/warning badge text if present (e.g. 'FINAL WARNING')."""
    badge = front_section.select_one("div.deadline-row span.deadline-badge")
    return badge.get_text(strip=True) if badge else ""

def extract_checksum(front_section: BeautifulSoup) -> str:
    """Extract full SHA256 checksum from data-checksum attribute if present."""
    row = front_section.select_one("div.checksum-row")
    return row.get("data-checksum", "") if row else ""

def extract_meta(front_section: BeautifulSoup) -> dict:
    """
    Extracts:
      - size (e.g., '1.6 GB (compressed)')
      - records (e.g., '20M Records')
      - updated_human (e.g., '23 Jan 2026')
    """
    res = {"size": "", "records": "", "updated_human": "", "updated_ts": ""}
    meta = front_section.select_one("div.meta")
    if not meta:
        return res

    spans = [s.get_text(" ", strip=True) for s in meta.find_all("span")]
    # Size: first span typically shows size with drive icon
    for s in spans:
        if re.search(r"\b(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB|bytes)\b", s, flags=re.IGNORECASE):
            res["size"] = s
            break

    # Records: e.g., '20M Records', '300K Records'
    for s in spans:
        if re.search(r"\b\d+(?:\.\d+)?\s*[KM]?\s*Records\b", s, flags=re.IGNORECASE) or \
           re.search(r"\b\d+(?:\.\d+)?[KM]?\s*Records\b", s, flags=re.IGNORECASE):
            res["records"] = s
            break

    # Updated (human): 'Updated: 23 Jan 2026'
    for s in spans:
        m = re.search(r"Updated:\s*(.+)$", s, flags=re.IGNORECASE)
        if m:
            res["updated_human"] = m.group(1).strip()
            res["updated_ts"] = to_micro_ts(res["updated_human"])
            break

    return res

def extract_info_popup(front_section: BeautifulSoup) -> dict:
    """
    Optional informational popup:
      - title from info-popup-inner h4
      - body paragraph(s) text
    """
    res = {"title": "", "text": ""}
    wrap = front_section.select_one("div.info-popup div.info-popup-inner")
    if not wrap:
        return res
    h4 = wrap.find("h4")
    p = wrap.find("p")
    if h4 and h4.get_text(strip=True):
        res["title"] = h4.get_text(" ", strip=True)
    if p and p.get_text(strip=True):
        res["text"] = p.get_text(" ", strip=True)
    return res

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

            # Try to discover host for 'website' / link normalization
            base_host = ""
            if BASE_URL:
                base_host = host_without_scheme(BASE_URL)
            if not base_host:
                base_host = get_hidden_service_host(soup)

            # Cards: standard listings and warning-card (active ransom warnings)
            cards = soup.select("article.card, article.warning-card")
            for card in cards:
                # Victim
                victim = extract_victim(card)

                # Published: prefer data-created (ISO) -> microsecond format
                created_raw = card.get("data-created", "") or ""
                published = to_micro_ts(created_raw)

                # Front section (wrapped in div.inner in the new layout)
                front = card.select_one("section.front")

                # Breach description paragraph
                breach_desc = extract_description_text(front) if front else ""

                # Meta fields (size, records, updated human + ts)
                meta_vals = extract_meta(front) if front else {"size": "", "records": "", "updated_human": "", "updated_ts": ""}

                # Info popup (optional)
                info_vals = extract_info_popup(front) if front else {"title": "", "text": ""}

                # Deadline / warning badge (e.g. "FINAL WARNING")
                deadline = extract_deadline(front) if front else ""

                # SHA256 checksum (optional)
                checksum = extract_checksum(front) if front else ""

                # Download link -> post_url
                dl = card.select_one("a.download-btn")
                href = dl.get("href", "") if dl else ""
                post_url = normalize_href(href, base_url=BASE_URL, fallback_host=base_host)

                # Website: store host only, no scheme
                website = base_host

                # Country unknown on this page
                country = ""

                # Build description string
                desc_parts = []
                if breach_desc:
                    desc_parts.append(breach_desc)
                if meta_vals.get("size"):
                    desc_parts.append(f"Size: {meta_vals['size']}")
                if meta_vals.get("records"):
                    desc_parts.append(f"Records: {meta_vals['records']}")
                if meta_vals.get("updated_human"):
                    desc_parts.append(f"Updated: {meta_vals['updated_human']}")
                if deadline:
                    desc_parts.append(f"Warning: {deadline}")
                if checksum:
                    desc_parts.append(f"SHA256: {checksum}")
                if info_vals.get("title"):
                    desc_parts.append(f"Note: {info_vals['title']}")
                if info_vals.get("text"):
                    info_text = info_vals["text"]
                    desc_parts.append(info_text)

                description = " | ".join([p for p in desc_parts if p])

                # Append record
                
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website="",                    # host only (no http/https)
                    published=str(published),           # 'YYYY-MM-DD HH:MM:SS.%f' or ''
                    post_url="",                  # absolute if possible
                    country=""
                )
              
                '''
                print('victim:', victim)
                print('desc.:', description)
                print('pub:', published)
                print('country:', country)
                print('-'*40)
                '''
        except Exception as e:
            errlog(group_name + " - parsing fail with error: " + str(e) + " in file: " + filename)

if __name__ == "__main__":
    main()
