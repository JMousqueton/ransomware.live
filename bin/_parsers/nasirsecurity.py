#!/usr/bin/env python3
# coding: utf-8
"""
Parser Nasir Security (page HTML avec newsData en JS) -> appender()
Signature appender (exemple) :
    def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
Règles :
 - Extrait chaque entrée de newsData (title, summary, date, url)
 - published : converti depuis "Oct 5, 2025" -> "%Y-%m-%d %H:%M:%S.%f"
 - website : premier lien HTTP(s) non-onion trouvé dans le header (si présent)
 - post_url : URL de l'item (résolue contre base_url)
 - country : vide (non présent dans cette page)
"""

import os, sys, re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse

from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

DATE_IN_FMT = "%b %d, %Y"
DATE_OUT_FMT = "%Y-%m-%d %H:%M:%S.%f"

def clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def parse_date(text: str) -> str:
    text = clean_text(text)
    try:
        dt = datetime.strptime(text, DATE_IN_FMT)
        return dt.strftime(DATE_OUT_FMT)
    except Exception:
        return ""

def first_http_non_onion(hrefs):
    for h in hrefs:
        try:
            u = urlparse(h)
            if u.scheme in ("http", "https") and ".onion" not in (u.netloc or ""):
                return h
        except Exception:
            continue
    return ""

def extract_news_items_from_js(html: str):
    """
    Extrait les objets {title, summary, date, url} depuis la variable JS newsData.
    On utilise une regex robuste multi-lignes et DOTALL.
    """
    items = []
    # Capture le bloc newsData = [ ... ];
    m = re.search(r'newsData\s*=\s*\[(.*?)\]\s*;', html, flags=re.S|re.I)
    if not m:
        return items
    block = m.group(1)

    # Pour chaque objet { ... } : on cherche title, summary, date, url (ordre quelconque)
    # On tolère des espaces et retours ligne, on n'impose pas la présence d'image/category.
    obj_iter = re.finditer(r'\{(.*?)\}', block, flags=re.S)
    for o in obj_iter:
        obj_txt = o.group(1)

        def grab(field):
            mm = re.search(rf'{field}\s*:\s*"([^"]*)"', obj_txt)
            return mm.group(1).strip() if mm else ""

        title = grab("title")
        summary = grab("summary")
        date = grab("date")
        url = grab("url")

        if title and url:
            items.append({
                "title": title,
                "summary": summary,
                "date": date,
                "url": url
            })
    return items

def main():
    # Nom du groupe depuis le nom du script (gestion des liens symboliques incluse)
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
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')

            # base_url pour résoudre les href relatifs comme pages/intro.html
            try:
                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))
            except Exception:
                base_url = ""

            # Website global (header) : premier http(s) non onion
            #header_links = []
            #for h in soup.find_all(['h3', 'a']):
            #    text = (h.get_text() or "").strip()
            #    if text.startswith("http"):
            #        header_links.append(text)
            #    if h.name == 'a' and h.has_attr('href') and h['href'].startswith("http"):
            #        header_links.append(h['href'])
            #website = first_http_non_onion(header_links)
            website = ""
            # Extraire les news depuis le JS
            news_items = extract_news_items_from_js(html)

            for it in news_items:
                post_title = clean_text(it["title"]).replace('Hacked','').strip()
                description = clean_text(it["summary"])
                published = parse_date(it["date"])
                post_url = urljoin(base_url, it["url"]) if base_url else it["url"]
                country = ""  # non disponible sur cette page

                # Évite les objets vides
                if not post_title:
                    continue
                if post_title == "First Statment":
                    continue

                """
                print('Victim:',post_title)
                print('description:',description)
                print('website:',website)
                print('published:',published)
                print('post_url:',post_url)
                print('country:',country)
                print('-',*40)
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
