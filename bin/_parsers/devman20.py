import os, re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def parse_usd(text):
    match = re.search(r'([\d.,]+)\s*(million|k|USD)', text, re.IGNORECASE)
    if match:
        value, unit = match.groups()
        value = float(value.replace(',', ''))
        if unit.lower() == 'million':
            return f"{int(value * 1_000_000)} USD"
        elif unit.lower() == 'k':
            return f"{int(value * 1_000)} USD"
        else:
            return f"{int(value)} USD"
    return text.strip()

def main():
    for filename in os.listdir(tmp_dir):
        if filename.startswith("devman-") and filename.endswith(".html"):
            try:
                html_path = tmp_dir / filename
                with open(html_path, "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")

                post_base = find_slug_by_md5("devman", extract_md5_from_filename(str(html_path)))

                cards = soup.find_all("div", class_="card")
                for card in cards:
                    title_tag = card.find("h2")
                    if not title_tag:
                        continue
                    victim = title_tag.get_text(strip=True).replace("Time Out", "").strip()

                    desc_tag = card.find("p")
                    if desc_tag:
                        desc = parse_usd(desc_tag.get_text())
                    else:
                        desc = ""

                    # Construct post URL using slug and sanitized victim name
                    post_url = f"{post_base}#{re.sub(r'[^a-zA-Z0-9\-]', '', victim.lower().replace(' ', '-'))}"
                    
                    appender(
                        victim=victim, 
                        group_name="devman", 
                        description=desc, 
                        website="", 
                        published="", 
                        post_url=post_url)
                    """
                    print('victim:', victim)
                    print('description:', desc)
                    print('post_url:', post_url)
                    print('*' * 40)
                    """
            except Exception as e:
                errlog(f"Devman 2.0 :Parser error in {filename}: {e}")
