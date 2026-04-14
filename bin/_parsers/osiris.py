#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, datetime, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def normalize_published(created_text: str) -> str:
    """
    Convert 'YYYY-MM-DD HH:MM' (optionally seconds)
    into 'YYYY-MM-DD 00:00:00.000000'
    """
    if not created_text:
        return ""

    created_text = created_text.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(created_text, fmt)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            continue
    return ""


def extract_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def extract_domains(text: str) -> str:
    if not text:
        return ""
    domains = re.findall(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", text)
    return domains[0] if domains else ""


def main():
    # Determine group_name from script name or symlink
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith(group_name + "-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

                # Each publication card
                cards = soup.select("div.sc-eJoXEY.eqpDCk")
                for card in cards:
                    # Victim name
                    victim_el = card.select_one("span.sc-dTvVRJ.cflNeq")
                    victim = extract_text(victim_el)

                    # Description
                    desc_el = card.select_one("div.sc-cpclqO span")
                    description = extract_text(desc_el)

                    # Extract domains from description
                    website = extract_domains(description)

                    # Published date
                    published_raw = ""
                    for span in card.select("span.sc-ggWZvA"):
                        txt = extract_text(span)
                        if re.match(r"\d{4}-\d{2}-\d{2}", txt):
                            published_raw = txt
                            break

                    published = normalize_published(published_raw)

                    # No per-victim URL visible
                    post_url = ""
                    country = ""

                    # Safety guard
                    if not victim:
                        continue

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description=description,
                        website=website,
                        published=published,
                        post_url=post_url,
                        country=country
                    )
                    


        except Exception as e:
            errlog(
                f"{group_name} - parsing fail with error: {e} in file: {filename}"
            )


if __name__ == "__main__":
    main
