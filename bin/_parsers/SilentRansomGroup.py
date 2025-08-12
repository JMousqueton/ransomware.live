import os, datetime, sys, re
from bs4 import BeautifulSoup
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

# Load .env
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
        original_path = os.path.abspath(original_path)
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                blocks = soup.select('.block_1')
                for block in blocks:
                    try:
                        company = block.find('td', string=re.compile("COMPANY:", re.IGNORECASE))
                        company = company.find_next_sibling('td').get_text(strip=True) if company else ""

                        info_cell = block.find('td', string=re.compile("COMPANY INFO:", re.IGNORECASE))
                        description = info_cell.find_next_sibling('td').get_text(strip=True) if info_cell else ""

                        #post_url = find_slug_by_md5(group_name, extract_md5_from_filename(filename)).replace('/news.html', '')
                        if "..." not in company:
                            appender(
                                victim=company,
                                group_name=group_name,
                                description=description,
                                website='',
                                published='',
                                post_url='',
                                country=''
                            )
                    except Exception as inner_e:
                        errlog(f"{group_name} - inner block parsing error: {inner_e} in file: {filename}")

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")

if __name__ == "__main__":
    main()
