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

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    cards = soup.select('.client-card')
                    for card in cards:
                        try:
                            name_tag = card.select_one('.client-name')
                            desc_tag = card.select_one('.client-description')
                            timer_tag = card.select_one('.client-timer')
                            btn_tag = card.select_one('.client-button')

                            victim = name_tag.text.strip() if name_tag else "N/A"
                            description = desc_tag.text.strip() if desc_tag else ""
                            if description == "No description provided":
                                description = ''
                            published_text = timer_tag.text.strip() if timer_tag else ""
                            post_url = ""

                            if btn_tag and 'onclick' in btn_tag.attrs:
                                onclick = btn_tag['onclick']
                                if "window.open('" in onclick:
                                    post_url = onclick.split("window.open('")[1].split("'")[0]

                            # Determine published date
                            if published_text.lower() == "published":
                                # We use countdown attribute as a pseudo timestamp
                                countdown_ts = card.get("data-countdown", "")
                                try:
                                    ts = int(countdown_ts)
                                    published_dt = datetime.datetime.utcfromtimestamp(ts / 1000)
                                    published = published_dt.strftime("%Y-%m-%d 00:00:00.000000")
                                except Exception:
                                    published = ""
                            else:
                                published = ""

                            appender(
                                victim=victim,
                                group_name=group_name,
                                description=description,
                                website="",
                                published=published,
                                post_url=post_url,
                                country=""
                            )
                            """
                            print('victim:',victim)
                            print('description:',description)
                            print('published:',published)
                            print('post_url:',post_url)
                            """
                        except Exception as inner_e:
                            errlog(group_name + ' - error parsing card: ' + str(inner_e))
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)

