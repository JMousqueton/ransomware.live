"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith("killsec-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")

            # If you still want to resolve the site root/slug later:
            try:
                address = find_slug_by_md5("killsec", extract_md5_from_filename(str(html_doc)))
            except Exception:
                address = ""

            # New card layout:
            # [header div] -> contains a flag <img src="/static/locales/XX.svg"> and a column with:
            #   <span>Title</span>
            #   <span>website.tld</span>
            # Next sibling <div> -> description (small text block).
            seen = set()

            for img in soup.find_all("img", src=True):
                if "/static/locales/" not in img["src"]:
                    continue

                header = img.find_parent("div")
                if not header:
                    continue

                # Column holding Title + Website (two stacked spans)
                info_col = header.find("div", class_=lambda c: c and "flex" in c and "flex-col" in c)
                if not info_col:
                    continue

                spans = info_col.find_all("span")
                if len(spans) < 2:
                    continue

                title = spans[0].get_text(strip=True)
                website = spans[1].get_text(strip=True)

                # Dedup in case multiple traversals hit the same card
                key = (title, website)
                if key in seen:
                    continue
                seen.add(key)

                # Country code from the flag filename, e.g. '/static/locales/us.svg' -> 'US'
                try:
                    flag_src = img["src"]
                    country = os.path.splitext(os.path.basename(flag_src))[0].upper()
                except Exception:
                    country = ""

                # Description: first meaningful next-sibling <div> with text
                description = ""
                sib = header.find_next_sibling("div")
                while sib and sib.name == "div":
                    text = sib.get_text(" ", strip=True) or ""
                    if text:
                        description = text
                        break
                    sib = sib.find_next_sibling("div")

                # No per-post URL or date visible on the cards (only a "Published" label)
                published = ""
                post_url = ""

                appender(title, "killsec", description, website, published, post_url, country)

        except Exception as e:
            errlog("killsec - parsing fail with error: " + str(e) + " in file: " + filename)

