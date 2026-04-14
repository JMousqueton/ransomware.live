"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |           |          |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, re
from bs4 import BeautifulSoup
from shared_utils import appender, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def extract_website(description):
    """Extract website from the beginning of description text."""
    first_token = description.split()[0] if description.split() else ""
    # Match domain-like patterns (no protocol, or with http/https)
    if re.match(r'^(https?://)?(www\.)?[\w\-]+\.[a-z]{2,}', first_token, re.IGNORECASE):
        # Strip protocol if present
        website = re.sub(r'^https?://', '', first_token).rstrip('/')
        return website
    return ""


def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('thegentlemen-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r', encoding='utf-8')
                soup = BeautifulSoup(file, 'html.parser')
                cards = soup.find_all("div", class_="card")
                for card in cards:
                    title_div = card.find("div", class_="card-title")
                    desc_div = card.find("div", class_="card-desc")
                    if not title_div or not desc_div:
                        continue

                    post_title = title_div.get_text(strip=True)
                    description = desc_div.get_text(strip=True)
                    website = extract_website(description)

                
                    appender(
                        victim=post_title,
                        group_name='thegentlemen',
                        description=description,
                        website=website,
                        published="",
                        post_url="",
                        country=""
                    )

                file.close()
        except Exception as e:
            errlog('thegentlemen - parsing fail with error: ' + str(e) + ' in file: ' + filename)
