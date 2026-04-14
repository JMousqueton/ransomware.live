"""
    BravoX - API parser
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="", extra_infos=[])
"""

import os, sys, requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, stdlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL   = "http://bravoxxtrmqeeevhl7gdh2yzvlrjxajr66d33c7ozosrccx4cz7cepad.onion"
API_BASE   = f"{BASE_URL}/scrapper-api"
AUTH_TOKEN = os.getenv("BRAVOX_API_TOKEN")
if not AUTH_TOKEN:
    errlog(f"bravox : BRAVOX_API_TOKEN not set in .env")
    sys.exit(1)
PAGE_LIMIT = 100

PROXIES = {
    "http":  "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

GROUP = "bravox"

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_date(iso: str) -> str:
    """Convert ISO 8601 datetime to 'YYYY-MM-DD HH:MM:SS.ffffff'."""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return ""

# ── API calls ─────────────────────────────────────────────────────────────────

def authenticate(session: requests.Session) -> bool:
    """POST /scrapper-api/auth/signin/{token} — sets Authorization header."""
    try:
        resp = session.post(f"{API_BASE}/auth/signin/{AUTH_TOKEN}", timeout=30)
        resp.raise_for_status()
        session_id = resp.json().get("session_id")
        if not session_id:
            errlog(f"{GROUP} : no session_id in auth response")
            return False
        session.headers["Authorization"] = session_id
        return True
    except Exception as e:
        errlog(f"{GROUP} : auth failed — {e}")
        return False


def fetch_posts(session: requests.Session) -> list:
    """Paginate POST /scrapper-api/posts/filter and return all raw records."""
    all_posts, page = [], 1
    while True:
        try:
            resp = session.post(
                f"{API_BASE}/posts/filter",
                json={"page": page, "limit": PAGE_LIMIT},
                timeout=60,
            )
            resp.raise_for_status()
            data  = resp.json()
            posts = data.get("data") or []
        except Exception as e:
            errlog(f"{GROUP} : fetch page {page} failed — {e}")
            break

        if not posts:
            break

        all_posts.extend(posts)

        if len(posts) < PAGE_LIMIT:
            break
        page += 1

    return all_posts

# ── Parser ────────────────────────────────────────────────────────────────────

def parse_post(raw: dict) -> None:
    """Map one raw API record to an appender() call. Skips unreleased posts."""
    if not raw.get("is_released", False):
        return

    campaign    = raw.get("campaign") or {}
    post_id     = raw.get("id", "")
    title       = campaign.get("name", "").strip()

    if not title:
        return

    website     = campaign.get("url", "")
    country     = (campaign.get("country") or "")[:2].upper()
    description = raw.get("description", "")
    published   = fmt_date(raw.get("release_at", ""))
    post_url    = f"{BASE_URL}/blog/{post_id}" if post_id else ""

    extra_infos = {}
    revenue = campaign.get("revenue")
    if revenue:
        extra_infos["revenue"] = revenue
    size = raw.get("size")
    if size:
        extra_infos["data_size"] = size
    files = raw.get("files")
    if files:
        extra_infos["files"] = files

    appender(title, GROUP, description, website, published, post_url, country) #, extra_infos)
    '''
    print('victim:',title)
    print('desc.:',description)
    print('website:',website)
    print('pub:', published)
    print('post_url:',post_url)
    print('country:',country)
    print('*'*40)
    '''
# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    session = requests.Session()
    session.proxies.update(PROXIES)
    session.headers.update({"Content-Type": "application/json"})

    if not authenticate(session):
        return

    raw_posts = fetch_posts(session)
    if not raw_posts:
        errlog(f"{GROUP} : no posts returned")
        return

    for raw in raw_posts:
        try:
            parse_post(raw)
        except Exception:
            errlog(f"{GROUP} : parsing fail")
