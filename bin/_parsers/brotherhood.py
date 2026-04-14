#!/usr/bin/env python3
# coding: utf-8
"""
Parser BrotherHood (HTML accordéon) -> appender()
Signature appender conforme à ton framework :
    def appender(post_title, group_name, description="", website="", published="", post_url="", country="")

Règles :
 - Ignore les entrées dont le titre est "Announcement"
 - Convertit le pays en code ISO-2 (pycountry + alias)
 - post_url : premier lien .onion trouvé
 - published : non présent dans le HTML
"""

import os, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
import pycountry
from urllib.parse import urljoin, urlparse
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def clean_text(s: str) -> str:
    """Nettoie le texte sans modifier les caractères spéciaux."""
    if not s:
        return ""
    return re.sub(r'\s+', ' ', s).strip()


def iso2(country_text: str) -> str:
    """Convertit un nom de pays en code ISO-2."""
    if not country_text:
        return ""
    c = country_text.strip()
    if re.fullmatch(r'[A-Za-z]{2}', c):
        return c.upper()
    aliases = {
        'USA': 'US',
        'United States': 'US',
        'United States of America': 'US',
        'UK': 'GB',
        'U.K.': 'GB',
        'England': 'GB',
        'South Korea': 'KR',
        'Korea': 'KR',
        'Russia': 'RU'
    }
    if c in aliases:
        return aliases[c]
    cclean = re.sub(r'[^A-Za-z \-]', '', c)
    try:
        return pycountry.countries.lookup(cclean).alpha_2
    except Exception:
        for cn in pycountry.countries:
            names = [cn.name]
            if hasattr(cn, 'official_name'):
                names.append(cn.official_name)
            if any(cclean.lower() == n.lower() for n in names):
                return cn.alpha_2
    return ""


def first_onion_link(hrefs) -> str:
    """Retourne le premier lien .onion trouvé dans la liste."""
    for h in hrefs:
        try:
            netloc = urlparse(h).netloc
            if ".onion" in netloc:
                return h
        except Exception:
            pass
        if ".onion/" in h or h.endswith(".onion/"):
            return h
    return ""


def main():
    # Détermine le nom du groupe à partir du nom du fichier
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

            # Base URL pour liens relatifs
            try:
                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))
            except Exception:
                base_url = ""

            # Chaque .accordion-item correspond à une victime
            for item in soup.select(".accordion-item"):
                btn = item.select_one(".accordion-header .accordion-button")
                post_title = clean_text(btn.get_text()) if btn else ""
                if not post_title:
                    continue

                # Ignore les entrées "Announcement"
                if post_title.strip().lower() == "announcement":
                    continue

                body = item.select_one(".accordion-body")
                if not body:
                    continue

                website = ""
                country = ""
                first_row = body.select_one(".row")

                if first_row:
                    cols = first_row.select(".col, .col-1")
                    if len(cols) >= 2:
                        a = cols[1].select_one("a[href]")
                        if a:
                            website = urljoin(base_url, a.get("href").strip()) if base_url else a.get("href").strip()
                        else:
                            website = clean_text(cols[1].get_text())
                    if len(cols) >= 4:
                        country_text = clean_text(cols[3].get_text())
                        country = iso2(country_text)

                # Description : bloc contenant "Contains:"
                description = ""
                contains_node = body.find(string=re.compile(r'Contains:', re.I))
                if contains_node:
                    description = clean_text(contains_node.parent.get_text())

                # post_url = premier lien .onion
                hrefs = [urljoin(base_url, a["href"].strip()) if base_url else a["href"].strip()
                         for a in body.find_all("a", href=True)]
                post_url = first_onion_link(hrefs)

                published = ""  # non présent dans le HTML

                """
                print('victim:',post_title)
                print('group_name:',group_name)
                print('description:',description)
                print('website:',website)
                print('published:',published)
                print('post_url:',base_url),
                print('country:',country)
                print('-'*40)


                # Appel à appender
                """
                appender(
                    post_title,
                    group_name,
                    description=description,
                    website=website,
                    published=published,
                    post_url="",
                    country=country
                )
            
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")


if __name__ == "__main__":
    main()
