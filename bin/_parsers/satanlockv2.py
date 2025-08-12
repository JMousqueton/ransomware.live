import os, datetime
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

    onion_base_url = "http://tzhwmgguyxrg6q3tu4q3gvopcjynrhw6ryx2bdl5ghisdkyunfua5xyd.onion"

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
                    cards = soup.select('.leak-card')

                    for card in cards:
                        h5 = card.find('h5')
                        p = card.find('p')
                        published_tag = card.find('div', class_='published')
                        link = card.get('href')

                        victim = h5.text.strip() if h5 else "N/A"
                        description = p.text.strip() if p else ""
                        post_url = f"{onion_base_url}{link}" if link else ""
                        published = published_tag.text.strip() if published_tag else ""

                        try:
                            published_dt = datetime.datetime.strptime(published, "%Y-%m-%d %H:%M:%S")
                            published_fmt = published_dt.strftime("%Y-%m-%d 00:00:00.000000")
                        except Exception:
                            published_fmt = ""

                        appender(
                            victim=victim,
                            group_name=group_name,
                            description=description,
                            website="",  # Optional: extract domain from victim if needed
                            published=published_fmt,
                            post_url=post_url,
                            country=""
                        )
                        #print(f"Victim: {victim}, Description: {description}, Published: {published_fmt}, Post URL: {post_url}")
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

if __name__ == "__main__":
    main()
