import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, find_slug_by_md5, extract_md5_from_filename
from urllib.parse import urljoin
from datetime import datetime


env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


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
        #try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    for article in soup.select("article.article-card"):
                        title_tag = article.select_one("h2 a")
                        date_tag = article.select_one("span.date")
                        desc_tag = article.select_one("p")

                        if not title_tag or not date_tag:
                            continue

                        name = title_tag.get_text(strip=True)
                        relative_url = title_tag.get("href", "").strip()
                        base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))) 
                        full_url = urljoin(base_url, relative_url) 
                        raw_date = date_tag.get_text(strip=True)
                        description = desc_tag.get_text(strip=True)
                        # Use current time for time part
                        try:
                            date_part = datetime.strptime(raw_date, "%Y-%m-%d").date()
                            now = datetime.now()
                            full_datetime = datetime.combine(date_part, now.time())
                            published_date = full_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            published_date = ""


                        appender(
                            victim=name,
                            group_name=group_name,
                            description=description,
                            website="",
                            published=published_date,
                            post_url=full_url,
                            country=""
                        )
        #except Exception as e:
        #    errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
