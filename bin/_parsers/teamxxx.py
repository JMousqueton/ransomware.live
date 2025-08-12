import os, datetime, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def country_name_to_code(name):
    try:
        return pycountry.countries.lookup(name.strip()).alpha_2.lower()
    except Exception:
        return ""

def extract_published(text):
    match = re.search(r'Published\s+(\d{1,2}/\d{1,2}/\d{4})', text)
    if not match:
        match = re.search(r'Published\s+(\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}Z)', text)
    if match:
        try:
            dt = datetime.datetime.strptime(match.group(1), "%d/%m/%Y %H:%M:%SZ")
        except ValueError:
            try:
                dt = datetime.datetime.strptime(match.group(1), "%d/%m/%Y")
            except ValueError:
                return ""
        return dt.strftime("%Y-%m-%d %H:%M:%S.000000")
    return ""

def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + '-'):
            continue

        try:
            html_doc = tmp_dir / filename
            with open(html_doc, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                cards = soup.find_all("div", class_="center1")

                for card in cards:
                    try:
                        letter_div = card.find("div", id="sonOne")
                        domain_div = card.find("div", id="sonTwo")

                        letter = letter_div.find("span").text.strip() if letter_div and letter_div.find("span") else ""
                        domain = domain_div.text.strip() if domain_div else ""

                        victim = f"{letter}{domain}"
            

                        p = card.find("p", id="TextColor")
                        raw_text = p.get_text(separator="\n").strip()

                        published = extract_published(raw_text)


                        links = p.find_all("a", href=True)
                        post_url = links[-1]['href'] if links else ""

                        description = p.get_text(separator="\n").strip().strip().replace('\n', ' ')

                        # Verbose output
                        print("=" * 60)
                        print(f"Victim:     {victim}")
                        print(f"Website:    {victim}")
                        print(f"Published:  {published}")
                        print(f"Post URL:   {post_url}")
                        print(f"Group:      {group_name}")
                        print("Description:\n", description[:300], "..." if len(description) > 300 else "")
                        print("=" * 60)
                    
                        appender(
                            victim=victim,
                            group_name=group_name,
                            description="",
                            website=victim,
                            published=published,
                            post_url=post_url,
                            country=""
                        )
                        
                    except Exception as e:
                        errlog(f"{group_name} - card parse error: {e} in file: {filename}")

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")

if __name__ == "__main__":
    main()
