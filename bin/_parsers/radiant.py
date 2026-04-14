#!/usr/bin/env python3
# coding: utf-8
"""
Parser Radiant (page 'Leaks' avec cartes .landing-box) -> appender()
Signature appender :
    def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def main():
    # Nom du groupe depuis le nom du script (gestion symlink incluse)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + '-'):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            html = str(soup)

            # Base URL pour résoudre les liens relatifs (ex: "Magna", "kido")
            try:
                base_slug = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))
                base_url = (base_slug or "").replace('/leaks', '')
            except Exception:
                base_url = ""

            # Chaque .landing-box = une entrée
            for box in soup.select('.landing-box'):
                title_el = box.select_one('h1.company-title')
                desc_el  = box.select_one('p.company-description')
                link_el  = box.select_one('a.view-more-link[href]')

                post_title = clean_text(title_el.get_text()) if title_el else ""
                if not post_title:
                    continue

                description = clean_text(desc_el.get_text()) if desc_el else ""
                post_url = urljoin(base_url, link_el['href'].strip()) if link_el else ""

                # Champs non fournis par cette page
                website = ""
                published = ""
                country = ""

                """
                print('victim:',post_title)
                print('description:',description)
                print('post_url:',post_url)
                print('-'*40)
                """
                appender(
                    post_title,
                    group_name,
                    description=description,
                    website=website,
                    published=published,
                    post_url=post_url,
                    country=country
                )
                #"""
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")

if __name__ == "__main__":
    main()
