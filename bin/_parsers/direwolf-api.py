import requests
import json
from datetime import datetime
from urllib.parse import urlparse

from shared_utils import stdlog, errlog, appender  # your own utilities

# -----------------------------
# API + Tor
# -----------------------------
API_URL = "http://direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd.onion/api/public/articles"
BASE_URL = "http://direwolfcdkv5whaz2spehizdg22jsuf5aeje4asmetpbt6ri4jnd4qd.onion"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

GROUP_NAME = "direwolf"  # <-- customize


# -----------------------------
# Utilities
# -----------------------------
import re
from datetime import datetime

def convert_timestamp(iso_timestamp):
    """Convert ISO timestamps (including nanosecond precision) to microsecond-accurate:
       'YYYY-MM-DD HH:MM:SS.xxxxxx'
    """
    if not iso_timestamp:
        return ""

    ts = iso_timestamp

    # ---- 1) Extract fractional seconds (if any) ----
    m = re.search(r"\.(\d+)", ts)
    if m:
        frac = m.group(1)

        # Normalize to microseconds → 6 digits
        if len(frac) > 6:
            frac = frac[:6]        # trim nanoseconds to microseconds
        else:
            frac = frac.ljust(6, "0")  # pad to 6 digits
        
        # Replace fractional part in the timestamp
        ts = re.sub(r"\.\d+", f".{frac}", ts)

    # ---- 2) Try parsing with timezone ----
    fmts = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f"
    ]

    for fmt in fmts:
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            continue

    errlog(f"[Timestamp] Failed to parse: {iso_timestamp}")
    return iso_timestamp




def clean_slug(url):
    """Extract hostname only (no scheme, no path)."""
    if not url:
        return ""
    try:
        host = urlparse(url).netloc
        return host.replace("www.", "").lower().strip()
    except:
        return ""


def parse_summary(summary_raw):
    """summary is a JSON string containing metadata."""
    try:
        return json.loads(summary_raw)
    except:
        return {}


# -----------------------------
# Fetch data
# -----------------------------
def fetch_articles():
    try:
        stdlog(f"Fetching Direwolf API: {API_URL}")

        r = requests.get(API_URL, proxies=PROXIES, timeout=30)
        r.raise_for_status()

        data = r.json()
        if "articles" not in data:
            errlog("Unexpected API format:")
            errlog(json.dumps(data, indent=4))
            return []

        stdlog(f"Fetched {len(data['articles'])} victims")
        return data["articles"]

    except Exception as e:
        errlog(f"Fetch error: {e}")
        return []


# -----------------------------
# Main parser
# -----------------------------
def main():
    articles = fetch_articles()
    if not articles:
        errlog("No victims received.")
        return

    for art in articles:

        summary = parse_summary(art.get("summary", ""))

        victim = summary.get("company_name", art.get("title"))
        website = summary.get("company_website", "")
        activity = summary.get("industry", "")
        data_size = summary.get("data_size", "")
        #gdpr = summary.get("gdpr_restricted", False)

        published = convert_timestamp(art.get("publish_time", ""))
        post_url = API_URL + '/' + str(art.get("id"))
        extra_infos = {
            "data_size": data_size,
            #"gdpr_restricted": gdpr,
            #"raw_summary": art.get("summary", "")
        }

        # append(victim, group_name, now, description, clean_slug(website),
        #        published, post_url, country, activity, doublons_infos, extra_infos)
    


        
        appender(
                            victim=victim,
                            group_name=GROUP_NAME,
                            description=activity,
                            website=clean_slug(website),
                            published=published,
                            post_url=post_url,
                            country="",
                            extra_infos=extra_infos
                        )
        """
        print('victim:',victim)
        print('desc:',activity)
        print('website:', clean_slug(website))
        print('published',published)
        print('post:',post_url)
        print('country:','')
        print('extra_info:',extra_infos)

        #stdlog(f"Added: {victim}")
        """

if __name__ == "__main__":
    main()
