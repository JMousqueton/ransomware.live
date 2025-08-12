import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from datetime import datetime
import pycountry
from rapidfuzz import process, fuzz

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def get_country_code(location):
    """Convert country name to 2-letter ISO code, handling typos."""
    if not location:
        return ""
    location = location.strip()
    # Try direct alpha_2 or alpha_3 code
    if len(location) == 2:
        c = pycountry.countries.get(alpha_2=location.upper())
        if c: return c.alpha_2
    if len(location) == 3:
        c = pycountry.countries.get(alpha_3=location.upper())
        if c: return c.alpha_2
    # Try exact/fuzzy name match
    try:
        c = pycountry.countries.search_fuzzy(location)
        if c: return c[0].alpha_2
    except LookupError:
        # Do fuzzy matching against all country names
        all_names = [country.name for country in pycountry.countries]
        best, score, _ = process.extractOne(location, all_names, scorer=fuzz.ratio)
        if score > 80:  # You can adjust the threshold
            match = pycountry.countries.get(name=best)
            if match: return match.alpha_2
    return ""


def convert_date(date_str):
    # Try parsing as mm/dd/yy first (PEAR uses 2-digit year), fallback to mm/dd/yyyy
    try:
        dt = datetime.strptime(date_str, "%m/%d/%y")
    except ValueError:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
    # Format as ISO 8601 with time and microseconds
    return dt.strftime("%Y-%m-%d 00:00:00.000000")


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


                    # Find all <details> blocks (one per victim)
                    for details in soup.find_all("details"):
                        summary = details.find("summary")
                        if not summary:
                            continue
                        
                        # Get the summary text, replacing newlines, and split by '|'
                        summary_text = summary.get_text(separator="|").replace('\n', '')
                        parts = [x.strip() for x in summary_text.split('|') if x.strip()]

                        # Victim name is the first non-empty part
                        victim_name = parts[0] if parts else "Unknown"

                        # Date: find first part that matches a date (mm/dd/yy or mm/dd/yyyy)
                        date = ""
                        for part in parts:
                            if re.match(r"\d{2}/\d{2}/\d{2,4}$", part):
                                date = part
                                break

                        # Description: all parts after the date, skipping "Leaked"
                        description = ""
                        if date and date in parts:
                            idx = parts.index(date)
                            after_date = [seg for seg in parts[idx+1:] if seg.lower() != "leaked"]
                            description = " ".join(after_date).strip()

                        # Convert the date if present
                        formatted_date = convert_date(date) if date else ""

                        details_text = details.get_text(separator="\n")
                        site = re.search(r"Site:\s*([^\n]+)", details_text)
                        industry = re.search(r"Industry:\s*([^\n]+)", details_text)
                        location = re.search(r"Location:\s*([^\n]+)", details_text)
                        revenue = re.search(r"Revenue:\s*([^\n]+)", details_text)
                        extra_infos = { 'Activity': industry.group(1).strip() if industry else '', 'Revenue': revenue.group(1).strip() if revenue else '' }
                        country = location.group(1).strip() if location else ''
                        if country:
                            country_code = get_country_code(country)
                        else:
                            country_code = ""

                        # Extract Details link (button)
                        post_url = ""
                        # Search for an <a> tag with text "Details"
                        details_a = details.find("a", string=re.compile(r"Details", re.I))
                        if details_a and details_a.has_attr('href'):
                            post_url =  find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))) + '/' + details_a['href']
                        """
                        print("="*60)
                        print(f"Victim Name: {victim_name}")
                        print(f"Date: {formatted_date}")
                        print(f"Description: {description}")
                        print(f"Site: {site.group(1).strip() if site else ''}")
                        print(f"Country: {country} ({country_code})")
                        print(f"Extrainfo: {extra_infos}")
                        print(f"Post_url: {post_url}")
                        """
                        appender(
                            victim=victim_name,
                            group_name=group_name,
                            description=description,
                            website=site.group(1).strip() if site else '',
                            published=formatted_date,
                            post_url=post_url,
                            country= country_code,
                            extra_infos=extra_infos
                        )
                        #"""
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
