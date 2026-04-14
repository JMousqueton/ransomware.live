"""
    TiMc parser - "Pixel Dashboard" site
    +-------------------------------------------+
    | Description | Website | published | post URL |
    +--------------------------+---------+---------+
    |      X      |    X    |           |          |
    +--------------------------+---------+---------+
    Rappel : def appender(victim, group_name, description="", website="", published="", post_url="", country="", extra_infos=[])
"""

import os, re
from bs4 import BeautifulSoup
from shared_utils import appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    script_path = os.path.abspath(__file__)
    group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Each victim is wrapped in div.pixel-border
            cards = soup.find_all("div", class_=lambda c: c and "pixel-border" in c)
            if not cards:
                errlog(f"{group_name} - no cards found in file: {filename}")
                continue

            for card in cards:
                # Victim name: span with text-phosphor (truncate flex-1)
                name_span = card.find("span", class_=lambda c: c and "truncate" in c and "flex-1" in c)
                victim = name_span.get_text(strip=True) if name_span else ""
                if not victim:
                    continue

                # Description: paragraph inside the card body
                desc_p = card.find("p", class_=lambda c: c and "font-[family-name:var(--font-terminal)]" in c)
                description = ""
                if desc_p:
                    raw = desc_p.get_text(separator="\n", strip=True)
                    # Strip leading ">" marker and "File preview: <url>" lines
                    raw = re.sub(r"^\s*>\s*", "", raw).strip()
                    description = re.sub(r"File preview:\s*https?://\S+\s*\n?", "", raw).strip()

                # Website: anchor with href
                website = ""
                link = card.find("a", href=True)
                if link:
                    href = link.get("href", "").strip()
                    if href.startswith("http"):
                        website = href

                appender(
                    victim=victim,
                    group_name=group_name,
                    description=description,
                    website=website,
                    published="",
                    post_url="",
                    country=""
                )

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")
