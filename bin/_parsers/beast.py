import os
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog

# Chargement des variables d'environnement
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    group_name = Path(__file__).stem  # "beast"

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + "-"):
            continue

        try:
            html_path = tmp_dir / filename
            with open(html_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

                cards = soup.select("div.catalog > a.card")
                for card in cards:
                    victim = card.find("h3").text.strip()
                    description = card.select_one(".card-text").get_text(" ", strip=True)

                    website_tag = card.select_one(".website")
                    website = website_tag.text.strip() if website_tag else ""

                    size_tag = card.select_one(".size")
                    size = size_tag.text.strip() if size_tag else ""

                    published = ""
                    raw_date = card.select_one(".date").text.strip()
                    for fmt in ("%d.%m.%Y", "%Y.%m.%d", "%d.%m.%y", "%m.%d.%Y"):
                        try:
                            dt = datetime.datetime.strptime(raw_date, fmt)
                            published = dt.strftime("%Y-%m-%d 00:00:00.000000")
                            break
                        except ValueError:
                            continue

                    relative_link = card.get("href", "")
                    base_slug = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_path)))
                    post_url = base_slug + relative_link

                    """
                    # Print each field
                    print(f"Victim      : {victim}")
                    print(f"Group       : {group_name}")
                    print(f"Published   : {published}")
                    print(f"Website     : {website}")
                    print(f"Post URL    : {post_url}")
                    print(f"Data Size   : {size}")
                    print(f"Description : {description}")
                    print("-" * 80)

                    # Appel à appender avec extra_infos
                    """
                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        published=published,
                        post_url=post_url,
                        country="",
                        extra_infos={"data_size": size}
                    )
             

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {str(e)} in file: {filename}")

if __name__ == "__main__":
    main()
