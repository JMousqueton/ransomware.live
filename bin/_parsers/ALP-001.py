#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog, find_slug_by_md5, extract_md5_from_filename, stdlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home    = os.getenv("RANSOMWARELIVE_HOME", "")
tmp_dir = Path(home + os.getenv("TMP_DIR", "./tmp"))


def normalize_desc(node) -> str:
    if node is None:
        return ""
    for br in node.find_all("br"):
        br.replace_with("\n")
    txt = node.get_text(separator=" ", strip=True)
    txt = re.sub(r"[ \t]*\n[ \t]*", "\n", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt).strip()
    return txt


def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + "-"):
            continue

        try:
            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")

            cards = soup.find_all("div", class_="article-item")
            if not cards:
                errlog(group_name + f" - no .article-item found in {filename}")
                continue

            base_post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

            for card in cards:
                try:
                    h3 = card.find("h3")
                    if not h3:
                        errlog(group_name + f" - missing <h3> in {filename}")
                        continue

                    victim   = h3.get_text(strip=True)
                    website  = victim  # h3 contains the domain
                    post_url = base_post_url + "#" + victim

                    # First <p> holds the metadata (Country, Revenue, Storage…)
                    paras = card.find_all("p")
                    description = normalize_desc(paras[0]) if paras else ""

                    # Extract Storage value for extra_infos
                    extra_infos = {"ransom": "", "data_size": ""}
                    storage_match = re.search(r"Storage:\s*(.+)", description, re.IGNORECASE)
                    if storage_match:
                        extra_infos["data_size"] = storage_match.group(1).strip()

                    # Append deadline if present
                    countdown = card.find("span", class_="countdown")
                    if countdown:
                        deadline = countdown.get("data-deadline", "")
                        if deadline:
                            description += f"\nDeadline: {deadline}"

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        post_url=post_url,
                        extra_infos=extra_infos,
                    )
                except Exception as ie:
                    errlog(group_name + f" - card parse error: {ie} in file: {filename}")
                    continue

        except Exception as e:
            errlog(group_name + " - parsing fail with error: " + str(e) + " in file: " + filename)


if __name__ == "__main__":
    main()
