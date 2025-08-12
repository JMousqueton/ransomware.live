import os, sys
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    script_path = os.path.abspath(__file__)
    group_name = os.path.basename(os.readlink(script_path) if os.path.islink(script_path) else script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_path = tmp_dir / filename
                with open(html_path, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
                
                for block in soup.find_all("div", class_="block"):
                    try:
                        content = block.find("div", class_="content")
                        if not content:
                            continue

                        victim_name = content.find("h3", class_="yellow-text").get_text(strip=True)
                        description_tag = content.find("p")
                        description = description_tag.get_text(strip=True) if description_tag else ""

                        # Extract .onion download link from spoiler-content
                        spoiler_link_tag = content.select_one(".spoiler-content a")
                        post_url = spoiler_link_tag["href"] if spoiler_link_tag and spoiler_link_tag.has_attr("href") else ""

                        slug = find_slug_by_md5(group_name, extract_md5_from_filename(Path(html_path).name))

                        appender(
                            victim=victim_name,
                            group_name=group_name,
                            description=description,
                            website="",  # Not provided
                            published="",  # Not provided
                            post_url=post_url or slug,  # fallback to slug if URL not found
                            country=""
                        )
                    except Exception as e:
                        errlog(f"{group_name} - block-level parse failed: {e} in file: {filename}")

        except Exception as e:
            errlog(f"{group_name} - parsing failed: {e} in file: {filename}")
