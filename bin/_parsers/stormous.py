import os
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

GROUP_NAME = "stormous"

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if not filename.startswith("stormous-"):
                continue

            html_doc = tmp_dir / filename
            with open(html_doc, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Each company entry is inside a "compact-table"
            for table in soup.select("div.compact-table table"):
                try:
                    # Extract company
                    company = ""
                    desc = ""

                    for tr in table.select("tbody tr"):
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = (tds[0].get_text(" ", strip=True) or "").strip().rstrip(":").lower()
                        val_td = tds[1]

                        if label == "company":
                            company = (val_td.get_text(" ", strip=True) or "").strip()

                        elif label == "description":
                            divs = val_td.find_all("div")
                            if divs:
                                parts = [
                                    d.get_text(" ", strip=True)
                                    for d in divs
                                    if d.get_text(strip=True)
                                ]
                                desc = " ".join(parts)
                            else:
                                desc = (val_td.get_text(" ", strip=True) or "").strip()

                    if company or desc:
                        appender(company, GROUP_NAME, desc, "", "", "", "")
                        #print('Company:', company)
                        #print('Description:', desc)
                        #print('-' * 40)

                except Exception as inner:
                    errlog(f"stormous - table parse error: {inner} in file: {filename}")

        except Exception as e:
            errlog("stormous - parsing fail with error: " + str(e) + " in file: " + filename)
