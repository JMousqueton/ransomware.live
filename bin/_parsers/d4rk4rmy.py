import os, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from datetime import datetime
from urllib.parse import urlparse

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def extract_domain(text):
    # Match the first URL in the string
    match = re.search(r'https?://[^\s]+', text)
    if match:
        url = match.group(0)
        domain = urlparse(url).netloc
        return domain
    return None

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
                for link in soup.find_all("a", href=True):
                    href = link["href"]

                    # Must be a real victim post
                    if ".onion" not in href or "/?p=" not in href:
                        continue

                    company = link.get_text(strip=True)
                    if not company or len(company) > 100 or "http" in company.lower():
                        continue

                    parent = link.find_parent()

                    # Find description nearby
                    desc_div = parent.find_next("div", class_="ultp-block-excerpt")
                    description = desc_div.get_text(" ", strip=True) if desc_div else ""
                    try:
                        domain = extract_domain(description)
                    except:
                        domain ='' 

                    appender(
                            victim=company.replace('[LEAKED]','').strip(),
                            group_name=group_name,
                            description=description,
                            website=domain,
                            published='',
                            post_url='',
                            country=''
                        )
                    #appender(company,group_name,description,domain)
                    

        except Exception as e:
            print(f"Error parsing row: {e}")
            continue