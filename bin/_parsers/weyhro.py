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
                html_doc= tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                for article in soup.find_all("article"):
                    date_element = article.find("time")
                    name_element = article.find("h2")
                    details_element = article.find("p")
                    link_element = article.find_parent("a")

                    date = date_element.text.strip()
                    name = name_element.text.strip()
                    details = details_element.text.strip()
                    link = link_element["href"]
                    link = find_slug_by_md5(group_name, extract_md5_from_filename(str(html_doc))).replace('/leaks','') + link
                    
                    # Convert date to required format
                    try:
                        date_obj = datetime.strptime(date, "%b %d, %Y")
                        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        formatted_date = ""
                    # Extract country from details (assuming format "$26M, Italy")
                    country_match = re.search(r",\s*(\w+)\s*$", details)
                    country = country_match.group(1) if country_match else "Unknown"
                    
                    # Convert country name to two-letter ISO code
                    country_code = "Unknown"
                    try:
                        country_obj = pycountry.countries.lookup(country)
                        country_code = country_obj.alpha_2
                    except LookupError:
                        country_code = ""
                    appender(
                        victim=name,
                        group_name=group_name,
                        description="",
                        website="",  # Optional, leave empty or populate if relevant data exists
                        published=formatted_date,
                        post_url=link,
                        country=country_code  # Optional, leave empty or populate if relevant data exists
                    )
                file.close()
        except Exception as e:
            errlog(group_name + ' - parsing fail with error: ' + str(e) + 'in file:' + filename)