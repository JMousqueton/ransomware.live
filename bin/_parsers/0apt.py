import os
import datetime
import json
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

# Optional base URL (e.g., onion address)
BASE_URL = os.getenv("BASE_URL", "").strip()

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def to_micro_ts(date_str: str) -> str:
    """
    Convert JS date strings like:
      'Feb 1, 2026 15:00:00'
    to 'YYYY-MM-DD HH:MM:SS.microseconds'
    """
    if not date_str:
        return ""
    try:
        dt = datetime.datetime.strptime(date_str.strip(), "%b %d, %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return ""

def strip_scheme(url: str) -> str:
    if not url:
        return ""
    return re.sub(r"^https?://", "", url.strip(), flags=re.IGNORECASE)

def host_without_scheme(url: str) -> str:
    if not url:
        return ""
    no_scheme = strip_scheme(url)
    return no_scheme.split("/", 1)[0]

def extract_timeline_data(soup: BeautifulSoup) -> dict:
    """
    Extract timelineData from embedded JS and return:
      { victim_name: published_ts }
    """
    published_map = {}

    scripts = soup.find_all("script")
    for script in scripts:
        if not script.string or "timelineData" not in script.string:
            continue

        m = re.search(
            r"const\s+timelineData\s*=\s*(\[.*?\]);",
            script.string,
            re.DOTALL
        )
        if not m:
            continue

        raw = m.group(1)

        # Convert JS object to valid JSON
        cleaned = re.sub(r"(\w+)\s*:", r'"\1":', raw)
        cleaned = cleaned.replace("'", '"')

        try:
            data = json.loads(cleaned)
            for item in data:
                victim = item.get("heading", "").strip()
                target = item.get("targetTime", "")
                published = to_micro_ts(target)
                if victim and published:
                    published_map[victim] = published
        except Exception:
            pass

    return published_map

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    # Derive group_name from script filename
    script_path = os.path.abspath(__file__)
    group_name = os.path.basename(script_path).replace(".py", "")

    # Iterate over downloaded HTML files
    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")

            container = soup.find("div", id="dynamic-container")
            if not container:
                continue

            # Extract published timestamps from JS
            published_map = extract_timeline_data(soup)

            cards = container.find_all("div", class_="card")
            for card in cards:
                h3 = card.find("h3")
                p = card.find("p")

                victim = h3.get_text(strip=True) if h3 else "N/A"
                description = p.get_text(" ", strip=True) if p else ""

                published = published_map.get(victim, "")

                post_url = BASE_URL
                website = host_without_scheme(BASE_URL)

                # ------------------------------------------------
                # DEBUG OUTPUT
                # ------------------------------------------------
                '''
                print('victim:', victim)
                print('post_url:', post_url)
                print('published:', published)
                print('website:', website)
                print('description:', description)
                print('-' * 40)
                '''
                # ------------------------------------------------
                # Append record
                # ------------------------------------------------
                
                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website=website,
                    published=published,
                    post_url=post_url,
                    country=""
                )

        except Exception as e:
            errlog(
                f"{group_name} - parsing fail with error: {e} in file: {filename}"
            )

if __name__ == "__main__":
    main()
