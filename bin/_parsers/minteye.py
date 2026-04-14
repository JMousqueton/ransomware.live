
import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def extract_text(el) -> str:
    """Safe text extraction with normalized spaces."""
    return el.get_text(" ", strip=True) if el else ""

def find_header_p(article) -> str:
    """
    Find the header <p> that contains the website and size.
    It usually is the <p> sibling of the <h2> inside the second inline-block <div>.
    Fallback: first <p> under the article that contains 'www.' or has a <strong>.
    """
    h2 = article.find("h2")
    if h2:
        # Prefer the <p> under the same container as the h2
        candidate = h2.find_next("p")
        if candidate:
            return candidate
    # Fallback: choose a sensible candidate among article <p> nodes
    for p in article.find_all("p", recursive=True):
        txt = extract_text(p)
        if "www." in txt or p.find("strong"):
            return p
    return None

def extract_website_from_text(text: str) -> str:
    """
    Extracts a domain-like token starting with 'www.' from text.
    Returns empty string if none found.
    """
    if not text:
        return ""
    m = re.search(r"\bwww\.[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    return m.group(0) if m else ""

def extract_size_from_header_p(p) -> str:
    """Returns size string from <strong> in the header <p>, e.g., '1.9 TB', '350 GB'."""
    if not p:
        return ""
    strong = p.find("strong")
    return extract_text(strong)

def parse_article(article, group_name: str):
    """
    Parse one <article> block and emit one appender record.
    If multiple download links exist, we choose the first as post_url by default.
    """
    # Victim name
    h2 = article.find("h2")
    victim = extract_text(h2) or "N/A"

    # Header <p> (contains website and size)
    header_p = find_header_p(article)
    header_text = extract_text(header_p) if header_p else ""
    website = extract_website_from_text(header_text)

    # Size (optional; we include in description as context)
    size_raw = extract_size_from_header_p(header_p)

    # Description: the next <p> after header_p (kept within the same article)
    description = ""
    if header_p:
        desc_p = header_p.find_next_sibling("p")
        description = extract_text(desc_p) if desc_p else ""
    else:
        # Fallback: longest textual paragraph under the article
        ps = article.find_all("p", recursive=False)
        if not ps:
            ps = article.find_all("p", recursive=True)
        # Prefer a paragraph that does not contain a size or www
        candidates = []
        for p in ps:
            t = extract_text(p)
            if t and "www." not in t and not p.find("strong"):
                candidates.append(t)
        if candidates:
            # Choose the longest candidate to avoid icon/small labels
            description = sorted(candidates, key=len, reverse=True)[0]

    # Download links (choose first by default)
    links = []
    for a in article.find_all("a", href=True):
        href = a["href"].strip()
        # Prefer onion links and/or zip files
        if ".onion" in href or href.lower().endswith(".zip"):
            links.append(href)
    post_url = links[0] if links else ""

    # Published date: not present in MintEye HTML
    published = ""  # Keep as empty string to match your baseline behavior

    # Country: not present
    country = ""

    # Optionally enrich description with size if present
    if size_raw and size_raw not in (description or ""):
        description = (description + ("\n\nSize: " + size_raw)).strip()

    # Emit record
    appender(
        victim=victim,
        group_name=group_name,
        description=description,
        website=website,
        published=published,
        post_url="",
        country=""
    )
    """
    print('Victim:',victim)
    print('DEsc.:',description)
    print('website:', website)
    print('published:', published)
    print('post_url:', post_url)
    print('country:',country)
    print('*'*40)
    """

def main():
    # Determine group_name from script path (symlink-aware), matching your baseline
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    # Iterate files in tmp_dir with prefix group_name + '-'
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    # Each victim entry is an <article> under <main>
                    articles = soup.find_all("article")
                    for article in articles:
                        parse_article(article, group_name)

        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

if __name__ == "__main__":
    main
