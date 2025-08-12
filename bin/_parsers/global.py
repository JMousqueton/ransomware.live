import os, datetime
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    script_path = os.path.abspath(__file__)
    group_name = os.path.basename(script_path).replace('.py','')
    if os.path.islink(script_path):
        group_name = os.path.basename(os.readlink(script_path)).replace('.py','')

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + '-'):
            continue

        html_doc = tmp_dir / filename
        try:
            with open(html_doc, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Each blog post is inside a flex row with two sections
                flex_rows = soup.find_all("div", style=lambda s: s and "flex-direction: row" in s)
                for row in flex_rows:
                    try:
                        left_col = row.find("div", style=lambda s: s and "padding: 48px 24px 24px" in s)
                        right_col = row.find_all("div")[-1]

                        victim_tag = left_col.find("h2")
                        date_tag = left_col.find("div", style=lambda x: x and "font-size: 0.875rem" in x)
                        desc_tag = left_col.find("p", style=lambda x: x and "line-height: 1.7" in x)
                        release_div = right_col.find("div", style=lambda x: x and "font-size: 0.8rem" in x)

                        victim = victim_tag.text.strip() if victim_tag else "N/A"
                        description = desc_tag.text.strip() if desc_tag else ""
                        published = date_tag.text.strip() if date_tag else ""
                        release_date = release_div.text.strip() if release_div else ""

                        # Format date
                        try:
                            published_dt = datetime.datetime.strptime(published, "%B %d, %Y")
                            published = published_dt.strftime("%Y-%m-%d 00:00:00.000000")
                        except Exception:
                            published = ""

                        # Push to storage
                       
                        appender(
                            victim=victim,
                            group_name=group_name,
                            description=description,
                            website="",
                            published=published,
                            country="",
                        )
                    except Exception as inner:
                        errlog(f"{group_name} - inner parse fail: {inner} in file: {filename}")

        except Exception as outer:
            errlog(f"{group_name} - parsing fail with error: {outer} in file: {filename}")
