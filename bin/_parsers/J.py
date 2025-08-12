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

                    articles = soup.find_all("article", class_="post-item")
                    for article in articles:
                        name_tag = article.find("h4", class_="post-item-title")
                        link_tag = name_tag.find("a") if name_tag else None
                        time_tag = article.find("time", class_="post-item-meta")

                        victim = link_tag.text.strip() if link_tag else "N/A"
                        post_url = link_tag.get("href") if link_tag else "N/A"
                        post_url = "http://twniiyed6mydtbe64i5mdl56nihl7atfaqtpww6gqyaiohgc75apzpad.onion" + post_url

                        published = time_tag.get("datetime") if time_tag else ""
                        if published:
                            try:
                                published_dt = datetime.datetime.fromisoformat(published.replace("Z", "+00:00"))
                                published = published_dt.strftime("%Y-%m-%d 00:00:00.000000")
                            except Exception:
                                published = ""

                        appender(
                            victim=victim,
                            group_name=group_name,
                            description="",
                            website="",
                            published=str(published),
                            post_url=post_url,
                            country=""
                        )
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file: ' + filename)
