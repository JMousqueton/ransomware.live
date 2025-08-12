import os, datetime, sys, re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    # Define the date format to convert to
    date_format = "%Y-%m-%d %H:%M:%S.%f"

    ## Get the ransomware group name from the script name
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py', '')
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py', '')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')

                    for article in soup.find_all('article', class_='post-card'):
                        try:
                            name_element = article.find('a', class_='logo')
                            date_element = article.find('p', class_='post-date')
                            description_element = article.find('p', class_='post-excerpt')
                            tags_element = article.find_all('span', class_='tag')

                            # Mandatory fields
                            name = name_element.text.strip() if name_element else "Unknown"
                            description = description_element.text.strip() if description_element else ""
                            post_date = date_element.text.strip() if date_element else ""

                            # Extract first website (optional, here none are direct)
                            website = ""

                            # Post URL - reconstruct it using the known method
                            post_url = name_element['href'] if name_element and name_element.has_attr('href') else ""
                            post_url = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))).replace('/leaks', '/') + post_url

                            # Published date conversion
                            try:
                                date_obj = datetime.strptime(post_date, "%B %d, %Y")
                                formatted_date = date_obj.strftime(date_format)
                            except Exception:
                                formatted_date = ""

                            # Country - trying from tags (fallback "Unknown")
                            country_code = ""
                            country_text = ""
                            for tag in tags_element:
                                tag_text = tag.text.strip()
                                # Try to detect country by tags if possible (rare here)
                                if tag_text.lower() in ["public services", "technology services", "food services", "softwares", "telecommunications"]:
                                    continue  # Skip generic tags
                                if re.match(r'.*\b(?:GB|Days|operation|targets)\b.*', tag_text, re.IGNORECASE):
                                    continue  # Skip size/operation tags
                                country_text = tag_text
                                break
                            try:
                                if country_text:
                                    country_obj = pycountry.countries.lookup(country_text)
                                    country_code = country_obj.alpha_2
                            except LookupError:
                                country_code = ""
                        

                            appender(
                                victim=name.replace(' company','').strip(),
                                group_name=group_name,
                                description=description,
                                website="",
                                published=formatted_date,
                                post_url=post_url,
                                country=""
                            )


                        except Exception as e:
                            errlog(f"{group_name} - parsing individual post failed with error: {str(e)} in file: {filename}")

        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {str(e)} in file: {filename}")

if __name__ == "__main__":
    main()
