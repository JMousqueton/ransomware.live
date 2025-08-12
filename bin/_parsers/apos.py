from bs4 import BeautifulSoup
import os, re
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, extract_md5_from_filename, find_slug_by_md5, errlog
import pycountry
from datetime import datetime

# Load environment
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def country_name_to_code(name):
    try:
        return pycountry.countries.lookup(name.strip()).alpha_2.lower()
    except Exception:
        return "??"

def parse_victims(html):
    soup = BeautifulSoup(html, "html.parser")
    """
    cards = soup.select("div.shadow-md.group")
    for card in cards:
        try:
            title = card.select_one("div.text-xl").text.strip()
            description = card.select_one("div.line-clamp-3")
            description = description.text.strip().replace('\n', ' ') if description else ''
            website = card.select_one("div.flex-row span").text.strip()
            updated = card.select_one("div.flex-row span:contains('Updated')")
            updated_text = updated.text.replace("Updated", "").strip() if updated else ""
            country = card.select("div.flex-row span")[-1].text.strip()
            country_code = country_name_to_code(country)

            # slug = find_slug_by_md5(website) or website
            appender(
                            victim=title,
                            group_name="apos",
                            description=description,
                            website=website,
                            published=str(updated_text),
                            post_url="",
                            country=""
            )
            #print('victim:',title)
            #print('description:',description)
            #print('website:',website)
            #print('published:', published)
            #print('*', *40)
        except Exception as e:
            errlog(f"APOS Parser error: {e}")
    """
    cards = soup.select("div.flex.flex-col.mt-3.mb-3.bg-stone-100.rounded-lg.px-4.pt-4.pb-3.shadow-md.group")
    for card in cards:
        try:
            name_elem = card.select_one("div.text-xl.font-semibold")
            name = name_elem.get_text(strip=True) if name_elem else None

            span_elems = card.select("div.flex.flex-row > span")
            domain = span_elems[0].get_text(strip=True) if len(span_elems) > 0 else None
            revenue = span_elems[1].get_text(strip=True) if len(span_elems) > 1 else None
            country = span_elems[2].get_text(strip=True) if len(span_elems) > 2 else None
            if country:
                country = country_name_to_code(country)
            else:
                country = "" 

            desc_elem = card.select_one("div.line-clamp-3.text-gray-600")
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Date parsing and formatting
            update_elem = card.find("span", string=re.compile(r"Updated "))
            date_str = update_elem.get_text(strip=True).replace("Updated ", "") if update_elem else None
            parsed_date = datetime.strptime(date_str, "%d-%b-%Y") if date_str else None
            full_date_str = parsed_date.strftime("%Y-%m-%d %H:%M:%S.%f") if parsed_date else None

            post_link_elem = card.select_one("a[href^='blog/']")
            post_url = post_link_elem['href'] if post_link_elem else None

            appender(
                            victim=name,
                            group_name="apos",
                            description=description,
                            website=domain,
                            published=full_date_str,
                            post_url="http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/" + post_url if post_url else None,
                            country=country
            )
        except Exception as e:
            errlog(f"APOS Parser error: {e} in card: {card}")


def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    for filename in os.listdir(tmp_dir):
        if filename.startswith(group_name + "-"):
            with open(tmp_dir / filename, "r", encoding="utf-8") as f:
                html = f.read()
                parse_victims(html)
