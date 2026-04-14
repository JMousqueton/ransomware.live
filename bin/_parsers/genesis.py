#!/usr/bin/env python3
# coding: utf-8
"""
GENESIS parser (listing .block-bg) — enrich only website & country via Tor

Process:
  1. Parse listing file locally from TMP_DIR
  2. For each victim, resolve post_url
  3. Query post_url via Tor SOCKS proxy
  4. Extract ONLY:
       - website  (from <p><strong>Website:</strong> ...)
       - country  (from footer tags like 'USA')
  5. Append record using appender()

Tor proxy settings come from .env:
  TOR_SOCKS_HOST=127.0.0.1
  TOR_SOCKS_PORT=9050
  TOR_TIMEOUT=25
  TOR_RETRIES=3
  TOR_SLEEP=1.0
"""

import os, re, time, random
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import tldextract

from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog


# ============ ENVIRONMENT & TOR CONFIG ============
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME", "")
tmp_dir = Path(home + os.getenv("TMP_DIR", ""))

TOR_SOCKS_HOST = os.getenv("TOR_SOCKS_HOST", "127.0.0.1")
TOR_SOCKS_PORT = int(os.getenv("TOR_SOCKS_PORT", "9050"))
TOR_TIMEOUT = int(os.getenv("TOR_TIMEOUT", "25"))
TOR_RETRIES = int(os.getenv("TOR_RETRIES", "3"))
TOR_SLEEP = float(os.getenv("TOR_SLEEP", "1.0"))


# ============ UTILITIES ============

def clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def to_std_dt(datestr: str) -> str:
    if not datestr:
        return ""
    try:
        return datetime.strptime(datestr.strip(), "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return ""

def build_tor_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=TOR_RETRIES,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "HEAD"]),
    )
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    socks = f"socks5h://{TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}"
    s.proxies.update({"http": socks, "https": socks})
    s.headers.update({
        "User-Agent": random.choice([
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/17.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
        ])
    })
    return s

def fetch_via_tor(session, url: str) -> str:
    try:
        r = session.get(url, timeout=TOR_TIMEOUT)
        if r.status_code == 200:
            return r.text
        errlog(f"GENESIS - Tor fetch {url} returned {r.status_code}")
    except Exception as e:
        errlog(f"GENESIS - Tor fetch failed for {url}: {e}")
    return ""

def extract_website_country(detail_html: str) -> tuple[str, str]:
    """Return (website, country) from detail page HTML"""
    website = ""
    country = ""
    soup = BeautifulSoup(detail_html, "html.parser")

    # Extract website
    for p in soup.find_all("p"):
        st = p.find("strong")
        if st and "website" in st.get_text(strip=True).lower():
            txt = p.get_text(separator=" ", strip=True)
            txt = re.sub(r"^\s*Website\s*:\s*", "", txt, flags=re.I)
            m = re.search(r"https?://\S+", txt)
            if m:
                website = m.group(0).rstrip(".,;)")
            else:
                a = p.find("a", href=True)
                if a:
                    website = a["href"].strip()
            break

    # Extract country from footer tags
    footer = soup.find("footer")
    if footer:
        aliases = {
            "USA": "US", "United States": "US", "United States of America": "US",
            "UK": "GB", "U.K.": "GB", "England": "GB",
            "Russia": "RU", "South Korea": "KR", "Korea": "KR"
        }
        for a in footer.select("a[href]"):
            label = a.get_text(strip=True)
            if label in aliases:
                country = aliases[label]
                break

    return website, country


# ============ MAIN PARSER ============

def main():
    # derive group name
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        real = os.path.abspath(os.readlink(script_path))
        group_name = os.path.basename(real).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    tor = build_tor_session()

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Base URL for relative hrefs
            try:
                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))
            except Exception:
                base_url = ""

            for sec in soup.select("section.block-bg"):
                title_el = sec.select_one("h2")
                if not title_el:
                    continue
                post_title = clean_text(title_el.get_text())
                if not post_title:
                    continue

                desc_el = sec.select_one(".not-prose p")
                description = clean_text(desc_el.get_text()) if desc_el else ""

                time_el = sec.find("time")
                published = to_std_dt(time_el.get_text()) if time_el else ""

                link_el = sec.select_one("a[href]")
                post_url = ""
                if link_el and link_el.has_attr("href"):
                    href = link_el["href"].strip()
                    post_url = urljoin(base_url, href) if base_url else href

                website = ""
                country = ""

                # Fetch post_url via Tor just to update website/country
                if post_url:
                    html_detail = fetch_via_tor(tor, post_url)
                    if html_detail:
                        website, country = extract_website_country(html_detail)
                    time.sleep(TOR_SLEEP)


                extracted = tldextract.extract(website)

                website = f"{extracted.domain}.{extracted.suffix}"
                """
                print('victim:', post_title)
                print('description:', description)
                print('published:', published)
                print('post_url:', post_url)
                print('country:', country)
                print('website:', website)
                """
                appender(
                    post_title,
                    group_name,
                    description=description,
                    website=website,
                    published=published,
                    post_url=post_url,
                    country=country
                )
                #"""
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")


if __name__ == "__main__":
    main()
