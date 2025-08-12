import requests
from datetime import datetime
import os,datetime,sys, re
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

URL = "http://ctyfftrjgtwdjzlgqh4avbd35sqrs6tde4oyam2ufbjch6oqpqtkdtid.onion" 
API_URL = URL + "/api/publication"
CATEGORY_URL = URL + "/api/category"

def format_datetime(dt_str):
    """Convert ISO string to 'YYYY-MM-DD HH:MM:SS.ssssss'"""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return dt_str

def extract_company_and_website(company_field):
    website = ""
    name = company_field
    m = re.match(r"^(.*?)(?:\s+(https?://|www\.)[^\s]+)?$", company_field.strip())
    if m:
        name = m.group(1).strip()
        if m.group(2):
            url_match = re.search(r"(https?://[^\s]+|www\.[^\s]+)", company_field)
            if url_match:
                website = url_match.group(1)
    return name, website

def fetch_category_mapping():
    resp = requests.get(CATEGORY_URL, proxies=PROXIES, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # categoryId -> name mapping
    return {cat['id']: cat['name'] for cat in data}

def main():
    print("Fetching category mapping...")
    cat_map = fetch_category_mapping()

    print("Fetching victim data...")
    resp = requests.get(API_URL, proxies=PROXIES, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    try:
        for idx, item in enumerate(data, 1):
            company_name, website = extract_company_and_website(item.get("company", ""))
            created_at = item.get("createdAt", "")[:19].replace("T", " ")
            updated_at = item.get("updatedAt", "")[:19].replace("T", " ")
            desc_html = item.get("description", "")
            desc_text = re.sub('<[^<]+?>', '', desc_html).strip()
            category_id = item.get('categoryId')
            category_name = cat_map.get(category_id, "Unknown")
            post_url = URL + "/publications/details/" + item.get("id")
            revenue = item.get('revenue')
            extra_infos = { 'Activity': category_name if category_name else '', 'Revenue': revenue }

            published_date = format_datetime(created_at)
            """
            #print(f"Victim #{idx}")
            print(f"ID           : {item.get('id')}")
            print(f"Company      : {company_name}")
            print(f"Website      : {website}")
            print(f"Status       : {item.get('status')}")
            print(f"Category     : {category_name} ") 
            print(f"Published    : {published_date}")
            print(f"\nDescription:\n{desc_text}")
            print(f"Post URL     : {post_url}")
            print(f"{'='*70}") 
            """
            appender(
                victim=company_name,
                group_name='blacknevas',
                description=desc_text,
                website=website,
                published=published_date,
                post_url=post_url,
                country="",
                extra_infos=extra_infos
            )
    except Exception as e:
        errlog('blacknevas' + ' - parsing fail with error: ' + str(e))
