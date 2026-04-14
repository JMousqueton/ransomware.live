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
            if filename.startswith(group_name + '-') and filename.endswith('.html'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeaugtifulSoup(file, 'html.parser')

                # Find the main table by class (new structure)
                table = soup.find('table', class_='_table_1462q_8')
                if not table:
                    continue

                # Get all rows, skip header
                rows = table.find('tbody').find_all('tr', recursive=False)
                for row in rows:
                    # Skip infoRow (details row)
                    if 'infoRow' in row.get('class', []):
                        continue
                    cells = row.find_all('td')
                    if len(cells) < 10:
                        continue
                    try:
                        # Company name (may be masked)
                        company_cell = cells[0]
                        company_p = company_cell.find('p', class_='_title_1462q_70')
                        Company = company_p.text.strip() if company_p else company_cell.text.strip()

                        # Date (format: YYYY-MM-DD)
                        Create_time_raw = cells[1].text.strip()
                        try:
                            Create_time = datetime.strptime(Create_time_raw, "%Y-%m-%d")
                            Create_time_str = Create_time.strftime("%Y-%m-%d %H:%M:%S.000000")
                        except Exception:
                            Create_time_str = Create_time_raw

                        # Website (may be <a> or text)
                        website_cell = cells[2]
                        website_a = website_cell.find('a')
                        Website = website_a.text.strip() if website_a else website_cell.text.strip()

                        # Country
                        Country = cells[3].text.strip()
                        if Country == 'USA':
                            Country = 'US'

                        # Revenue
                        Revenue = cells[4].text.strip()

                        # Employees (may be masked)
                        Employees = cells[5].text.strip()

                        # Status/Type
                        Status = cells[6].text.strip()

                        # Data size
                        Data = cells[7].text.strip()

                        # Views (may be masked)
                        Views = cells[8].text.strip()

                        # Post URL (may be in details row, not in main row)
                        Post_URL = ''
                        # Try to find a link in the company cell (details link)
                        link_tag = company_cell.find('a', class_='link')
                        if link_tag and link_tag.has_attr('href'):
                            Post_URL = link_tag['href']
                        # If not, try to find in the details row (next sibling)
                        next_row = row.find_next_sibling('tr')
                        if next_row and 'infoRow' in next_row.get('class', []):
                            info_link = next_row.find('a', class_='link')
                            if info_link and info_link.has_attr('href'):
                                Post_URL = info_link['href']

                        extra_infos = {
                            'data_size': Data,
                            'employees': Employees,
                            'status': Status,
                            'views': Views
                        }

                        print(f"Victim: {Company}")
                        print(f"  Website: {Website}")
                        print(f"  Revenue: {Revenue}")
                        print(f"  Country: {Country}")
                        print(f"  Data Leaked: {Data}")
                        print(f"  Employees: {Employees}")
                        print(f"  Status: {Status}")
                        print(f"  Views: {Views}")
                        print(f"  Post URL: {Post_URL}")
                        print(f"  Discovered: {Create_time_str}")
                        print("-" * 80)

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
            print(f"Error parsing file: {e}")
            continue