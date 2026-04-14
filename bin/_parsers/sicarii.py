
import os
import datetime
import sys
import re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

# Load environment (.env at ../.env, same as your example)
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# Optional: if you want to build absolute URLs for relative links like "/pdf.pdf"
# Put BASE_URL in your .env (e.g., BASE_URL="http://example.onion")
BASE_URL = os.getenv("BASE_URL", "").strip()  # e.g., http://xxxx.onion

def normalize_url(href: str) -> str:
    """
    Convert relative hrefs (e.g., '/pdf.pdf') to absolute if BASE_URL is set.
    Otherwise, return the original or 'N/A' if not usable.
    """
    if not href:
        return "N/A"
    href = href.strip()
    if BASE_URL and href.startswith("/"):
        return BASE_URL.rstrip("/") + href
    # If href is already absolute or BASE_URL not available, return as-is
    return href

def extract_victim_from_h2(h2_text: str) -> str:
    """
    Expected format (Hebrew):
      'דליפה: Triad Packaging - 102GB נתונים'
    We extract the victim name between 'דליפה:' and the first dash (if present).
    Fallbacks handled elsewhere if this fails.
    """
    if not h2_text:
        return ""
    text = h2_text.strip()

    # Try to capture victim after 'דליפה:' up to the first dash (or end of string)
    # Handle different dash variants (ASCII -, en dash – , em dash —)
    m = re.search(r"דליפה[:：]?\s*(.+?)(?:\s*[-–—]\s*|$)", text)
    if m:
        return m.group(1).strip()

    # If regex fails, heuristics: remove 'דליפה' and trim
    text = re.sub(r"^דליפה[:：]?\s*", "", text).strip()
    # If there's a dash, take the part before it
    parts = re.split(r"\s*[-–—]\s*", text)
    return parts[0].strip() if parts else text

def extract_victim_from_logo(logo_alt: str) -> str:
    """
    Fallback to the company logo alt text (e.g., 'Triad Packaging Logo').
    We'll remove common suffixes like 'Logo' (case-insensitive).
    """
    if not logo_alt:
        return ""
    victim = logo_alt.strip()
    victim = re.sub(r"\s*logo\s*$", "", victim, flags=re.IGNORECASE).strip()
    return victim

def main():
    # Derive group_name from this script's real path (handling symlinks), same as your example
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    # Iterate over files in tmp_dir with the naming convention: {group_name}-*
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename

                # Read HTML as UTF-8 (Hebrew-safe)
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                # Each post is in <div class="blog-post">
                posts = soup.find_all("div", class_="blog-post")
                for post in posts:
                    # --- Victim extraction ---
                    victim = ""
                    # Primary: <h2> text like "דליפה: Triad Packaging - 102GB נתונים"
                    h2 = post.find("h2")
                    if h2:
                        victim = extract_victim_from_h2(h2.get_text(strip=True))

                    # Fallback: company logo alt "Triad Packaging Logo"
                    if not victim:
                        logo_img = post.find("div", class_="company-logo")
                        if logo_img:
                            img = logo_img.find("img")
                            if img and img.get("alt"):
                                victim = extract_victim_from_logo(img.get("alt"))

                    if not victim:
                        victim = "N/A"

                    # --- Post URL ---
                    # There is no dedicated post link; use first proof/download link if present
                    first_dl = post.find("a", class_="download-link")
                    post_url = normalize_url(first_dl.get("href") if first_dl else "N/A")

                    # --- Description ---
                    # Combine all <p> tags within the post to form a description
                    paragraphs = [p.get_text(" ", strip=True) for p in post.find_all("p")]
                    description = " ".join([t for t in paragraphs if t])

                    # Optional: include countdown/timer if present
                    timer = post.find("div", class_="timer")
                    if timer:
                        t_text = timer.get_text(strip=True)
                        if t_text:
                            description = (description + f" | Countdown: {t_text}").strip()

                    # --- Published ---
                    # Not present in the provided HTML; leave empty (to align with your example behavior)
                    published = ""

                    # --- Website / Country ---
                    # No specific website present; BASE_URL (from .env) can be used if desired
                    website = BASE_URL if BASE_URL else ""
                    country = ""  # Cannot safely infer from Hebrew text; leave empty

                    # Append the record
                    
                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        published=str(published),
                        post_url="",
                        country=country
                    )
                    """
                    print(f"Victim: {victim}")
                    print(f"Post URL: {post_url}")
                    print(f"Description: {description}")
                    print(f"Published: {published}")
                    print(f"Website: {website}")
                    print(f"Country: {country}")
                    print("-" * 40)
                    """
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

if __name__ == "__main__":
    main()