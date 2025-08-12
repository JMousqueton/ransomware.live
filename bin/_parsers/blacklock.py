# From Template v4 - 202412827
# +----------------------------------------------+
# | Description | Website | published | post URL |
# +-----------------------+-----------+----------+
# |       X     |         |           |     X    |
# +-----------------------+-----------+----------+

import os
import re
import json
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from datetime import datetime

# Load environment
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def extract_projects_json(html_content):
    """Extracts the `projects = [...]` JSON string from inline script."""
    match = re.search(r"const projects = (\[.*?\]);", html_content, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError("Could not extract `projects` JSON.")

def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + "-") and filename.endswith(".html"):
                filepath = tmp_dir / filename
                with open(filepath, "r", encoding="utf-8") as file:
                    html = file.read()

                soup = BeautifulSoup(html, "html.parser")
                script_tags = soup.find_all("script", {"type": "text/babel"})

                for script in script_tags:
                    if "const projects =" in script.text:
                        victims = extract_projects_json(script.text)
                        for entry in victims:
                            victim = entry.get("fullname", "").strip()
                            description = entry.get("desc", "").strip()
                            post_url = entry.get("url1", "").strip()
                            website = entry.get('name', '').strip()
                            url = entry.get('url1', '')

                            ts = entry.get("ts", 0)
                            published = ""

                            # Only use timestamp if it's realistic (e.g., after year 2000)
                            if ts and ts > 946684800:  # 2000-01-01 00:00:00 UTC
                                published = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")

                            if url:
                                post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(filename))) + str(url) 
                            else: 
                                url = ''
                            #print(f"Victim       : {victim}")
                            #print(f"Description  : {description}")
                            #print(f"published    : {published}")
                            #print(f"Website      : {entry.get('name', '')}")
                            #print(f"Image        : {entry.get('img', '')}")
                            #print(f"Counter      : {entry.get('counter', '')}")
                            #print(f"Timestamp    : {entry.get('ts', '')} ({datetime.utcfromtimestamp(entry.get('ts', 0)).isoformat()})")
                            #print(f"Release      : {entry.get('release', '')} ({datetime.utcfromtimestamp(entry.get('release', 0)).isoformat()})")
                            #print(f"URL1 Label   : {entry.get('urlname1', '')}")
                            #print(f"URL1         : {entry.get('url1', '')}")
                            #print(f"URL2 Label   : {entry.get('urlname2', '')}")
                            #print("*" * 40)
                            appender(
                                victim=victim,
                                group_name=group_name,
                                description=description,
                                website=website,
                                published=published,
                                post_url=post_url,
                                country=''
                            )
                        break  # Only parse the first matching script block
        except Exception as e:
            errlog(f"{group_name} - parsing failed with error: {str(e)} in file: {filename}")
