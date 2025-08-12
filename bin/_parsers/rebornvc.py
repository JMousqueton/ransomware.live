import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

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

                cards = soup.select(".card")
                for card in cards:
                    company = card.select_one(".company-header")
                    details = card.select_one(".victim-details")
                    ransom = card.select_one(".ransom-amount")

                    if company:
                        victim_name = company.get_text(strip=True)
                        description = details.get_text(strip=True)
                        ransom_amount = ransom.get_text(strip=True)

                            
                        extra_infos = { 'ransom': ransom_amount }


                    appender(
                        victim=victim_name,
                        group_name=group_name,
                        description=description,
                        website="",
                        published="",
                        post_url="",
                        country="",
                        extra_infos=extra_infos
                    )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
