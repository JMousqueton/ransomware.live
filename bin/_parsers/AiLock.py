"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |     X     |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os, re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def extract_website(text):
    """Extract first domain-like token from a string."""
    match = re.search(r'\b[\w-]+\.(?:com|net|org|co\.\w+|io|gov|edu|no|kr|de|uk|fr|nl|au|ca|ch|be|se|dk|fi|pl|es|it|ru|cn|br)\b', text)
    return match.group(0) if match else ""


def main():

    ## Get the ransomware group name from the script name
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py', '')
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                file = open(html_doc, 'r')
                soup = BeautifulSoup(file, 'html.parser')
                file.close()

                base_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

                # Build modal lookup: data-id -> description text
                modals = {}
                for modal_div in soup.find_all('div', id=re.compile(r'^modal\d+$')):
                    modal_id = modal_div['id'].replace('modal', '')
                    desc_p = modal_div.find('p', string=lambda t: t and len(t.strip()) > 10)
                    if not desc_p:
                        # fallback: pick second <p> inside modal-content
                        modal_content = modal_div.find('div', class_='modal-content')
                        if modal_content:
                            paragraphs = modal_content.find_all('p')
                            # skip the date paragraph
                            for p in paragraphs:
                                if p.find('b') is None and len(p.get_text(strip=True)) > 10:
                                    desc_p = p
                                    break
                    modals[modal_id] = desc_p.get_text(strip=True) if desc_p else ""

                cards = soup.find_all('div', class_='news-card')
                for card in cards:
                    name_tag = card.find('h3')
                    if not name_tag:
                        continue
                    name = name_tag.get_text(strip=True)

                    date_span = card.find('span', class_=re.compile(r'nes-text'))
                    date_text = date_span.get_text(strip=True) if date_span else ""

                    published = ""
                    if date_text and date_text.lower() != "coming soon":
                        try:
                            published = datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00.000000")
                        except ValueError:
                            published = ""

                    # Card description paragraph (contains domain + data size)
                    card_paragraphs = card.find_all('p')
                    card_desc = ""
                    for p in card_paragraphs:
                        if not p.find('b') and not p.find('span'):
                            card_desc = p.get_text(strip=True)
                            break

                    website = extract_website(card_desc)

                    # Get detailed description from modal
                    btn = card.find('button', attrs={'data-id': True})
                    data_id = btn['data-id'] if btn else None
                    description = modals.get(data_id, card_desc) if data_id else card_desc
                    if not description:
                        description = card_desc


                    appender(
                        victim=name,
                        group_name=group_name,
                        description=description,
                        website=website,
                        published=published,
                        post_url="",
                        country=""
                    )
                    '''
                    print('victim:', name)
                    print('desc.:', description)
                    print('website:', website)
                    print('published:', published)
                    print('---')
                    '''
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
