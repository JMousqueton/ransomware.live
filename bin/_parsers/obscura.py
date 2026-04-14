
import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def normalize_published(created_text: str) -> str:
    """
    Convert 'YYYY-MM-DD HH:MM' (optionally seconds) into 'YYYY-MM-DD 00:00:00.000000'.
    Returns empty string if parsing fails.
    """
    if not created_text:
        return ""
    created_text = created_text.strip()
    # Try known formats
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(created_text, fmt)
            # Normalize to midnight with microseconds
            normalized = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            return normalized.strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            continue
    return ""

def extract_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""

def main():
    # Determine group_name from script (supports symlink same as your base parser)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    # Iterate all temp files that match the group prefix
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    # Each victim card sits under: <div class="cards"><div class="card">...</div></div>
                    cards = soup.select("div.cards > div.card")
                    for card in cards:
                        header = card.select_one(".card-header")
                        desc = card.select_one(".card-desc")

                        # Header spans
                        title_el = header.select_one("span.title") if header else None
                        domain_el = header.select_one("span.domain") if header else None
                        industry_el = header.select_one("span.industry") if header else None
                        size_el = header.select_one("span.size") if header else None
                        created_el = header.select_one("span.created") if header else None
                        status_el = header.select_one("span.status") if header else None

                        title = extract_text(title_el)
                        domain = extract_text(domain_el)
                        description = extract_text(desc)
                        created_raw = extract_text(created_el)

                        # Map to your appender schema
                        victim = title or domain or "N/A"
                        website = domain or ""
                        published = normalize_published(created_raw)
                        post_url = ""  # No per-card link in provided HTML
                        country = ""   # Not present in HTML

                        # Optional: Skip non-victim announcement cards
                        # e.g., if you want to exclude "New Obscura 2.0!" marketing posts
                        # uncomment the next lines:
                        # if not domain and "Obscura" in victim:
                        #     continue

                        appender(
                            victim=victim,
                            group_name=group_name,
                            description=description,
                            website=website,
                            published=published,
                            post_url=post_url,
                            country=country
                        )
                    

                        print('Victim:',victim)
                        print('Description:',description)
                        print('Published:',published)
                        print('website:',website)
                        print('*'*40)
                        

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

if __name__ == "__main__":
    main
