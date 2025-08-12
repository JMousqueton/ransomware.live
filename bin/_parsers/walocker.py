import os, datetime
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def country_name_to_code(name):
    #try:
        country = pycountry.countries.lookup(name.strip())
        return country.alpha_2.lower()
    #except Exception:
        return ""


def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + '-'):
            continue

        try:
            html_doc = tmp_dir / filename
            with open(html_doc, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                cards = soup.find_all("div", class_="company-card")
                for card in cards:
                    try:
                        victim = card.find("div", class_="company-name").text.strip()
                        website_tag = card.find("div", class_="website")
                        website = website_tag.text.strip() if website_tag else ""

                        country_tag = card.find("div", class_="country")
                        country_raw = country_tag.text.strip() if country_tag else ""
                        if country_raw == "Cambodian":
                            country_raw = "Cambodia"
                        country = country_name_to_code(country_raw)


                        #views_tag = card.find("div", class_="views")
                        #views = views_tag.text.strip() if views_tag else ""

                        dates = card.find("div", class_="dates")
                        added, published = "", ""
                        if dates:
                            for date_item in dates.find_all("div", class_="date-item"):
                                text = date_item.text.strip().lower()
                                if "added" in text:
                                    added = text.replace("added:", "").strip() + " 00:00:00.000000"
                                elif "publication date" in text:
                                    published = text.replace("publication date:", "").strip() + " 00:00:00.000000"

                        onclick = card.get("onclick", "")
                        post_url = ""
                        if "detail.php?id=" in onclick:
                            post_id = onclick.split("id=")[-1].strip("')")
                            post_url = f"{find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))}/detail.php?id={post_id}"

                        appender(
                            victim=victim,
                            group_name=group_name,
                            description="",
                            website=website,
                            published=published,
                            post_url=post_url,
                            country=country.upper()
                        )
                        """
                        print('victim:',victim)
                        print('website:',website)
                        print('published:',published)
                        print('post:',post_url)
                        print('coutnry:',country_raw)
                        print('country code:',country)
                        """
                    except Exception as e:
                        errlog(f"{group_name} - card parse error: {e} in file: {filename}")

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")

if __name__ == "__main__":
    main()
