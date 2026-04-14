import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def normalize_date(raw):
    """
    Converts formats like 9.11.2025 to ISO 2025-11-09 00:00:00.000000.
    If the date is in the future → return empty (ignored).
    """
    try:
        dt = datetime.datetime.strptime(raw, "%d.%m.%Y")
        now = datetime.datetime.now()
        if dt > now:
            return ""  # ignore future dates
        return dt.strftime("%Y-%m-%d 00:00:00.000000")
    except:
        return ""

def normalize_size(raw):
    """
    Converts sizes like '184.55 GB' or '73.54 GB'.
    Normalizes MB → GB.
    """
    try:
        m = re.search(r'([0-9\.]+)\s*(GB|TB|MB)', raw, re.I)
        if not m:
            return ""
        value = float(m.group(1))
        unit = m.group(2).upper()

        if unit == "MB":
            value = value / 1024
            unit = "GB"

        return f"{value} {unit}"
    except:
        return ""

def main():
    script_path = os.path.abspath(__file__)

    # Handle symlink logic for locating group name
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    # Parsing TMP_DIR files for this group
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + "-"):
                html_doc = tmp_dir / filename

                with open(html_doc, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")

                articles = soup.find_all("div", class_="article")

                for article in articles:
                    a = article.find("a")
                    if not a:
                        continue

                    # Title
                    h2 = a.find("h2")
                    victim = h2.get_text(strip=True) if h2 else "N/A"

                    # URL (relative → full onion URL)
                    post_path = a.get("href", "").strip()
                    post_url = (
                        find_slug_by_md5(group_name, extract_md5_from_filename(Path(html_doc).name)).replace('/articles','') + post_path
                        if post_path
                        else ""
                    )

                    # Extract text block
                    p = a.find("p")
                    p_text = p.get_text(" ", strip=True) if p else ""

                    # Leak date (9.11.2025)
                    date_match = re.search(r'Leak date\s+(\d{1,2}\.\d{1,2}\.\d{4})', p_text)
                    leak_date_raw = date_match.group(1) if date_match else ""
                    published = normalize_date(leak_date_raw)

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description="",
                        website="",
                        published=str(published),
                        post_url=post_url,
                        country=""
                    )

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")
