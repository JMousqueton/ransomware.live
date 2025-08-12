import os
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from shared_utils import appender, extract_md5_from_filename, find_slug_by_md5, errlog

# Load environment
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
        group_name = os.path.basename(original_path).replace('.py', '')
    else:
        group_name = os.path.basename(script_path).replace('.py', '')

    for filename in os.listdir(tmp_dir):
        if filename.startswith(group_name + '-'):
            html_doc = tmp_dir / filename
            try:
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                cards = soup.select(".company-card")
                for card in cards:
                    try:
                        title = card.select_one(".company-header h3").text.strip()

                        #raw_date = card.select_one(".countdown-timer")["data-deadline"]
                        #discovered = datetime.fromisoformat(raw_date).strftime("%Y-%m-%d %H:%M:%S.%f")

                        #image_url = card.select_one(".company-image img")["src"]

                        domain_text = ""
                        for row in card.select(".info-row"):
                            label = row.select_one(".info-label")
                            if label and "domain" in label.text.lower():
                                domain_text = row.get_text(strip=True).replace(label.get_text(strip=True), "").strip()
                                break

                        size = ""
                        for row in card.select(".info-row"):
                            label = row.select_one(".info-label")
                            if label and "data size" in label.text.lower():
                                size = row.get_text(strip=True).replace(label.get_text(strip=True), "").strip()
                                break
                        
                        ransom = ""
                        for row in card.select(".info-row"):
                            label = row.select_one(".info-label")
                            if label and "payment status" in label.text.lower():
                                ransom = row.get_text(strip=True).replace(label.get_text(strip=True), "").strip()
                                break


                        post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc)))

                        extra_infos = {
                            "data_size": size.replace("(encrypted)", "").strip()     if size else "",
                            "ransom": ransom.replace("Unpaid (", "").replace("unpaid (","").replace(" requested)", "" ) if ransom else "",
                        }

                        # print(f"[+] {title} | {domain_text} | {discovered} | {post_url} | {extra_infos}")
                        
                        appender(
                            group_name=group_name,
                            victim=title,
                            # img=image_url,
                            post_url=post_url,
                            description=domain_text,
                            # html_path=str(html_doc),
                            extra_infos=extra_infos
                        )
                    
                    except Exception as e:
                        errlog(f"[!] Error parsing entry in {filename}: {e}")
            except Exception as e:
                errlog(f"[!] Error opening file {filename}: {e}")

if __name__ == "__main__":
    main()
