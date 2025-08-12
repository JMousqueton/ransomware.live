import os, datetime, sys, re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def to_country_code(country_string):
    try:
        country_name = country_string.split(",")[0].strip()
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except:
        return ""


def main():
    # Date conversion (not used here, but defined if needed later)
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    # Determine the ransomware group name from the script filename
    script_path = os.path.abspath(__file__)
    group_name = os.path.basename(script_path).replace('.py', '')
    if os.path.islink(script_path):
        original_path = os.path.realpath(script_path)
        group_name = os.path.basename(original_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    for pkg in soup.select("div.block__package"):
                        name_tag = pkg.select_one("span:contains('Name:') + p")
                        name = name_tag.get_text(strip=True) if name_tag else "Unknown"

                        description_parts = []

                        rev_tag = pkg.select_one("span:contains('Revenue:') + p")
                        if rev_tag:
                            description_parts.append(f"Revenue: {rev_tag.get_text(strip=True)}")

                        type_tag = pkg.select_one("span:contains('Type:') + p")
                        if type_tag:
                            description_parts.append(f" Type: {type_tag.get_text(strip=True)}")
 
                        size_tag = pkg.select_one("span:contains('Size:') + p")
                        if size_tag:
                            description_parts.append(f" Size: {size_tag.get_text(strip=True)}")

                        date_tag = pkg.select_one("span:contains('Date:') + p")
                        if date_tag:
                            raw_date = date_tag.get_text(strip=True)
                            try:
                                parsed_date = datetime.strptime(raw_date, "%m/%d/%Y %H:%M")
                                formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S.%f")
                            except:
                                formatted_date = ""
                        else:
                            formatted_date = ""

                        country_tag = pkg.select_one("span:contains('Сountry:') + p")
                        country_raw = country_tag.get_text(strip=True) if country_tag else ""
                        country_code = to_country_code(country_raw)
                        
                        full_description = "\n".join(description_parts)

                        filling = pkg.find_parent("div", class_="filling")
                        a_tag = filling.find("a", class_="stretched-link") if filling else None
                        href = a_tag["href"] if a_tag and a_tag.has_attr("href") else ""
                        post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))) + href

                        #print('victim:', name)
                        #print('group_name:', group_name)
                        #print('description:', full_description)
                        #print('published:', formatted_date)
                        #print('post_url:', post_url)
                        #print('country:', country_code)
                        #print('*' * 20)
                        appender(
                            victim=name,
                            group_name=group_name,
                            description=full_description,
                            website="",  # no direct website listed
                            published=formatted_date,  # no exact published timestamp
                            post_url=post_url,
                            country=country_code,
                        )

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")
