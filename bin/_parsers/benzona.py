import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# ----------------------------------------------------
# Convert DD.MM.YYYY → YYYY-MM-DD 00:00:00.000000
# BUT skip future dates
# ----------------------------------------------------
def convert_date(date_str):
    try:
        dt = datetime.datetime.strptime(date_str.strip(), "%d.%m.%Y")
        now = datetime.datetime.now()

        # ignore if in the future
        if dt > now:
            return ""

        return dt.strftime("%Y-%m-%d 00:00:00.000000")
    except Exception:
        return ""

# ----------------------------------------------------
# Convert "500gb" → "500 GB"
# Convert "1tb"  → "1 TB"
# ----------------------------------------------------
def normalize_data_size(raw):
    if not raw:
        return ""

    s = raw.strip().lower().replace(" ", "")

    # match number + unit (gb/tb/mb)
    m = re.match(r"(\d+)(gb|tb|mb)", s)
    if not m:
        return raw  # leave untouched if unknown format

    number, unit = m.groups()
    return f"{number} {unit.upper()}"


# ----------------------------------------------------
# MAIN PARSER
# ----------------------------------------------------
def main():
    script_path = os.path.abspath(__file__)

    # Determine group name via symlink or filename
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    for filename in os.listdir(tmp_dir):

        try:
            if filename.startswith(group_name + "-"):
                html_doc = tmp_dir / filename

                with open(html_doc, "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")

                # Victims inside: <div class="victim-card">
                cards = soup.find_all("div", class_="victim-card")

                for card in cards:

                    # victim domain
                    h3 = card.find("h3")
                    victim = h3.text.strip() if h3 else "N/A"

                    data_size = ""
                    ransom = ""
                    leak_date = ""

                    for p in card.find_all("p"):
                        text = p.get_text(strip=True)

                        if text.startswith("Data:"):
                            raw_ds = text.replace("Data:", "").strip()
                            data_size = normalize_data_size(raw_ds)

                        elif text.startswith("Ransom:"):
                            ransom = text.replace("Ransom:", "").strip()

                        elif text.startswith("Leak Date:"):
                            raw_date = text.replace("Leak Date:", "").strip()
                            leak_date = convert_date(raw_date)

                    # -------------------------------
                    # EXTRA INFOS (conditional ransom)
                    # -------------------------------
                    extra_infos = {
                        "data_size": data_size
                    }

                    if ransom:  # only add ransom if not empty
                        extra_infos["ransom"] = ransom

                    appender(
                        victim=victim,
                        group_name=group_name,
                        description="",
                        website=victim,
                        published=str(leak_date),
                        post_url="",
                        country="",
                        extra_infos=extra_infos
                    )

        except Exception as e:
            errlog(f"{group_name} parsing fail: {str(e)} in file {filename}")


if __name__ == "__main__":
    main()
