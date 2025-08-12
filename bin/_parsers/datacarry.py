import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog
import re

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def flag_emoji_to_iso2(flag: str) -> str:
    if len(flag) != 2:
        return ""
    return ''.join([chr(ord(c) - 0x1F1E6 + ord('A')) for c in flag])

def clean_victim_text(raw_text):
    # Remove embedded <br/> or literal 'br/' and split emoji
    cleaned = raw_text.replace("br/", "").strip()
    # Match trailing country flag emoji
    match = re.search(r'([\U0001F1E6-\U0001F1FF]{2})$', cleaned)
    if match:
        flag = match.group(1)
        name = cleaned.replace(flag, '').strip()
        iso2 = flag_emoji_to_iso2(flag)
        return name, iso2
    return cleaned.strip(), ""

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
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    for a_tag in soup.select("a.icon[href$='.zip']"):
                        victim_div = a_tag.select_one("div")
                        if not victim_div:
                            continue

                        raw_text = victim_div.get_text(separator='', strip=True)
                        name, country_iso2 = clean_victim_text(raw_text)

                        appender(
                            victim=name,
                            group_name=group_name,
                            description="",
                            website="",
                            published="",
                            post_url="",
                            country=country_iso2
                        )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
