import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import find_slug_by_md5, appender, extract_md5_from_filename, errlog
import tldextract
import pycountry


# Load environment variables
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def country_name_to_code(name):
    try:
        country = pycountry.countries.get(name=name)
        return country.alpha_2 if country else None
    except:
        return None

def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
                    
                    victim_blocks = soup.find_all('div', style=lambda s: s and 'background-color: azure' in s)
                    
                    for block in victim_blocks:
                        try:
                            name_tag = block.find('div', class_='companyName').find('a')
                            victim = name_tag.text.strip()
                            description = ""
                            post_url = find_slug_by_md5(group_name, extract_md5_from_filename(filename))
                            
                            info_div = block.find('div', style=lambda s: s and 'padding-left: 10px' in s)
                            website = ""
                            published = ""
                            country = ""
                            
                            for item in info_div.find_all('div', recursive=False):
                                text = item.get_text(strip=True)
                                if text.startswith("Industry:"):
                                    description = text.replace("Industry:", "").strip()
                                elif text.startswith("Location:"):
                                    country = text.replace("Location:", "").strip()
                                elif text.startswith("Publish Date:"):
                                    published = text.replace("Publish Date:", "").strip()
                                elif text.startswith("URL:"):
                                    website_tag = item.find('a')
                                    if website_tag:
                                        website = website_tag['href']
                            
                            extracted = tldextract.extract(website)
                            domain = f"{extracted.domain}.{extracted.suffix}"
                            published = ""
                            
                            appender(
                                victim=victim,
                                group_name=group_name,
                                description=description,
                                website=domain,
                                published="",
                                post_url=post_url,
                                country=country_name_to_code(country)
                            )
                            
                            #print(f"Victim: {victim}, Description: {description}, Website: {domain}, Published: {published}, Post URL: {post_url}, Country: {country_name_to_code(country)}")
                        
                        except Exception as ve:
                            errlog(f"{group_name} - parsing victim block failed: {ve} in file: {filename}")
        except Exception as e:
            errlog(f"{group_name} - parsing fail with error: {e} in file: {filename}")

if __name__ == '__main__':
    main()
