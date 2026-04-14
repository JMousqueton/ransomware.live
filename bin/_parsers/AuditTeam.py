"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, sys
import requests
import pycountry
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}


def fetch_entity(entity_url):
    """Fetch description and country from an entity page via Tor."""
    description = ''
    country = ''
    try:
        resp = requests.get(entity_url, proxies=proxies, timeout=(30, 30))
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        desc_tag = soup.find('div', class_='desc-published')
        if desc_tag:
            description = desc_tag.get_text(strip=True)
        flag_tag = soup.find('span', class_='flag-text')
        if flag_tag:
            country_name = flag_tag.get_text(strip=True)
            try:
                match = pycountry.countries.get(name=country_name)
                if not match:
                    match = pycountry.countries.search_fuzzy(country_name)[0]
                if match:
                    country = match.alpha_2
            except LookupError:
                errlog('AuditTeam - could not resolve country: ' + country_name)
    except Exception as e:
        errlog('AuditTeam - failed to fetch entity page ' + entity_url + ': ' + str(e))
    return description, country


def main():
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
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

                with open(html_doc, 'r') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                for card in soup.find_all('div', class_='card'):
                    title_tag = card.find('div', class_='title')
                    if not title_tag:
                        continue

                    onclick = card.get('onclick', '')
                    entity_id = ''
                    if "window.open('/entity/" in onclick:
                        entity_id = onclick.split("window.open('/entity/")[1].split("'")[0]

                    # For resolved/paid entries, use entity ID as victim name
                    if 'title-resolved' in title_tag.get('class', []):
                        if not entity_id:
                            continue
                        victim = f'Paid Victim {entity_id}'
                    else:
                        victim = title_tag.get_text(strip=True)
                    if not victim:
                        continue

                    # Extract discovery date
                    published = ''
                    for meta in card.find_all('div', class_='meta-info'):
                        text = meta.get_text(strip=True)
                        if text.startswith('DISCOVERY DATE:'):
                            date_str = text.replace('DISCOVERY DATE:', '').strip()
                            try:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                published = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                pass

                    # Build post URL
                    post_url = ''
                    if entity_id and base_url:
                        post_url = base_url.rstrip('/') + '/entity/' + entity_id

                    # Fetch description and country from entity page
                    description, country = fetch_entity(post_url) if post_url else ('', '')

                    appender(victim, group_name, description, '', published, post_url, country)
                    '''
                    print(f'victim    : {victim}')
                    print(f'group     : {group_name}')
                    print(f'published : {published}')
                    print(f'post_url  : {post_url}')
                    print(f'country   : {country}')
                    print(f'description: {description}')
                    print('-' * 60)
                    '''
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
