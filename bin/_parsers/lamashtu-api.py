"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys, json, requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, stdlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
db_dir = Path(home + os.getenv("DB_DIR"))

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}

TARGET_GROUP = "lamashtu"
PAGE_LIMIT   = 20


def get_base_url() -> str:
    with open(db_dir / "groups.json") as f:
        groups = json.load(f)
    group = next((g for g in groups if g.get("name") == TARGET_GROUP), None)
    if not group:
        errlog(f"{TARGET_GROUP}: group not found in groups.json")
        sys.exit(1)
    locations = group.get("locations", [])
    slug = locations[0].get("slug", "").rstrip("/") if locations else ""
    if not slug:
        errlog(f"{TARGET_GROUP}: no slug in locations")
        sys.exit(1)
    return slug


def parse_date(value: str) -> str:
    """Convert ISO 8601 datetime to 'YYYY-MM-DD HH:MM:SS.ffffff' (victims.json format)."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return value


def fetch_posts_page(base_url: str, page: int) -> dict:
    url = f"{base_url}/api/posts"
    try:
        resp = requests.get(url, params={"page": page, "limit": PAGE_LIMIT},
                            proxies=proxies, timeout=(60, 60))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        errlog(f"{TARGET_GROUP}: failed to fetch page {page}: {e}")
        return {}


def main():
    base_url = get_base_url()

    page = 1
    while True:
        data = fetch_posts_page(base_url, page)
        posts = data.get("posts", [])
        if not posts:
            break

        for post in posts:
            title     = post.get("title", "").strip()
            website   = post.get("website", "")
            desc      = post.get("short_desc", "")
            published = parse_date(post.get("publish_at", post.get("created_at", "")))
            post_id   = post.get("id", "")
            post_url  = f"{base_url}/post/{post_id}" if post_id else ""

            
            appender(title, TARGET_GROUP,
                     description=desc,
                     website=website,
                     published=published,
                     post_url=post_url)
            '''
            print('victim:',title)
            print('website:',website)
            print('pub:',published)
            print('Desc.',desc)
            print('post_url:',post_url)
            print('*'*40)
            '''
        total = data.get("total", 0)
        limit = data.get("limit", PAGE_LIMIT)
        if page * limit >= total:
            break
        page += 1
