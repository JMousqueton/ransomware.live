import os, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from datetime import datetime

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

                # Expected headers
                expected_headers = [
                    "Create time", "Company", "Website", "Revenue",
                    "Country", "Data", "Status", "Views", "Countdown"
                ]


                tables = soup.find_all("table")
                for table in tables:
                    headers = [th.text.strip() for th in table.find_all("th")]
                    if headers[:len(expected_headers)] == expected_headers:
                        rows = table.find_all("tr")
                        for row in rows[1:]:  # Skip header row
                            cells = row.find_all("td")
                            if len(cells) < 9:
                                continue

                            try:
                                Create_time_raw = cells[0].text.strip()
                                Create_time = datetime.strptime(Create_time_raw, "%Y-%m-%d %H:%M")
                                Create_time_str = Create_time.strftime("%Y-%m-%d %H:%M:%S.%f")
                                company_cell = cells[1]
                                post_link_tag = company_cell.find("a")
                                post_url = post_link_tag.get("hx-post", "").strip() if post_link_tag else ""
                                
                                company_cell = cells[1]
                                Company = company_cell.text.strip()
                                Website = cells[2].text.strip()
                                Revenue = cells[3].text.strip()
                                Country = cells[4].text.strip()
                                if Country == 'USA':
                                    Country = 'US'
                                Data = cells[5].text.strip()
                                Post_URL = company_cell.find("a").get("hx-post", "").strip() if company_cell.find("a") else ""
                                if Post_URL:
                                    Post_URL = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))+ Post_URL
                                    Post_URL = Post_URL.replace('//', '/')
                                extra_infos = { 'data_size': Data }
                                """
                                print(f"Victim: {Company}")
                                print(f"  Website: {Website}")
                                print(f"  Revenue: {Revenue}")
                                print(f"  Country: {Country}")
                                print(f"  Data Leaked: {Data}")
                                print(f"  Post URL: {Post_URL}")
                                print(f"  Discovered: {Create_time_str}")
                                print("-" * 80)

                                """
                                appender(
                                    victim=Company,
                                    group_name=group_name,
                                    description='',
                                    website=Website,
                                    published=Create_time_str,
                                    post_url=Post_URL,
                                    country=Country,
                                    extra_infos=extra_infos
                                )
                                
                                                          
                            except Exception as e:
                                print(f"Error parsing row: {e}")
                                continue
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue