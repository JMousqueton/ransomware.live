import os, datetime, sys, re
import pycountry
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, extract_md5_from_filename, find_slug_by_md5

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def convert_country_to_iso2(name):
    """Convert country name to ISO ALPHA-2."""
    if not name:
        return ""
    try:
        country = pycountry.countries.lookup(name)
        return country.alpha_2
    except Exception:
        return ""

def convert_date(date_str):
    """Convert MM/DD/YYYY -> YYYY-MM-DD 00:00:00.000000"""
    try:
        dt = datetime.datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d 00:00:00.000000")
    except Exception:
        return ""

def main():
    script_path = os.path.abspath(__file__)
    group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

            cards = soup.select("div[data-slot='card']")
            if not cards:
                errlog(f"{group_name} - no cards found in file: {filename}")
                continue

            md5 = extract_md5_from_filename(str(html_doc))

            for card in cards:
                # victim/company
                h3 = card.select_one("h3.text-xl")
                victim = h3.get_text(strip=True) if h3 else "N/A"

                # published date
                date_tag = card.select_one("div.flex.items-center.justify-between > span.text-xs")
                published_raw = date_tag.get_text(strip=True) if date_tag else ""
                published = convert_date(published_raw)

                # description
                desc = card.select_one("p.text-muted-foreground")
                description = desc.get_text(strip=True) if desc else ""

                # country
                country_tag = card.find("span", string="Country:")
                if country_tag:
                    country_val = country_tag.find_next("span").get_text(strip=True)
                    country = convert_country_to_iso2(country_val)
                else:
                    country = ""


                if victim != "N/A":
                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website="",
                        published=published,
                        post_url="",
                        country=country
                    )
                """

                print('victim:',victim)
                print('description:',description)
                print('published:',published)
                print('country:',country)
                print('*'*40)
                """
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")
