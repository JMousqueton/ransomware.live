"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |         |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def is_fqdn(name):
    """Check if the given name is a Fully Qualified Domain Name (FQDN)."""
    return bool(re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", name))

def main():

    # Define the date format to convert to
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    
    ## Get the ransomware group name from the script name 
    script_path = os.path.abspath(__file__)
    # If it's a symbolic link find the link source 
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py','')
    # else get the script name 
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py','')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name+'-'):
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                articles = soup.find_all('div', id=lambda x: x and x.startswith('article_'))
                for card in soup.find_all("div", class_="card-body"):
                    title = card.find("h5", class_="card-title").text.strip()

                    # Extract description
                    description_tag = card.find_all("p")
                    description = ""
                    for tag in description_tag:
                        if "Description:" in tag.text:
                            description = tag.get_text(" ", strip=True).replace('Description:', '')
                            break

                    # Extract publication time
                    publication_time_tag = card.find("span", attrs={"data-countdown-publication-time": True})
                    publication_time = publication_time_tag["data-countdown-publication-time"] if publication_time_tag else ""

                    # Extract revenue
                    revenue_tag = card.find("p", string=lambda text: text and "Revenue:" in text)
                    revenue = revenue_tag.text.replace("Revenue:", "").strip() if revenue_tag else ""

                    # Extract company name correctly
                    company_name = ""
                    for tag in card.find_all("p"):
                        if "Company name:" in tag.text:
                            company_name = tag.get_text(" ", strip=True).replace("\n", " ").strip()
                            break

                    # Extract article link
                    link_tag = card.find("a", href=True)
                    if link_tag:
                        link = find_slug_by_md5(group_name, extract_md5_from_filename(Path(html_doc).name))  + link_tag["href"].replace('articles/','')
                    else:
                        link = ""
                    

                    # Assign website and victim based on FQDN check
                    clean_company_name = company_name.replace("Company name: ", "").strip()
                    if is_fqdn(clean_company_name):
                        website = clean_company_name.replace('www.','')
                        victim = title
                    elif is_fqdn(title):
                        victim = clean_company_name
                        website = title.replace('www.','')
                    else:
                        victim = title
                        website = ""
                    
                    appender(victim, group_name, description,website,'',link)
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + ' in file:' + filename)
