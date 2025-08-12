import os, sys
import urllib3
import requests
import json
from datetime import datetime
from shared_utils import appender
from pathlib import Path
from dotenv import load_dotenv
import tldextract
import pycountry

# Load environment
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# Onion URL for Silent group
onion_url = 'http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/api/company/'

# Disable certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tor proxy settings
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def country_name_to_code(name):
    try:
        country = pycountry.countries.get(name=name)
        return country.alpha_2 if country else None
    except:
        return None

def fetch_json_from_onion_url(url):
    try:
        response = requests.get(url, proxies=proxies, verify=False, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching from Silent group:", e)
        return None
    return response.json()

def convert_date(unix_timestamp=None):
    if not unix_timestamp:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    dt = datetime.fromtimestamp(unix_timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def loop_disclosures():
    company_id = 1
    while True:
        disclosure_url = f"http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/api/disclosures/?company_id={company_id}"
        try:
            response = requests.get(disclosure_url, proxies=proxies, verify=False, timeout=30)
            if company_id == 2000: #response.status_code == 500:
                print("Stopped at ")
                print(f"Stopped at company_id={company_id} due to HTTP 500.")
                break
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching disclosure for company_id={company_id}:", e)
            break

        results = data.get("results", [])
        if results:
            disclosure = results[0]
            company_name = disclosure.get("company_name", "")
            description = f'Not claimed yet {disclosure.get("description", "")}'
            file_size = disclosure.get("filesSizes", "")
            print(f"[{company_id}] Company: {company_name} | Description: {description} | Size: {file_size}")
            extra_infos = { 'data_size': file_size }
            post_url= f"http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/api/disclosures/?company_id={company_id}"
            appender(company_name, 'silent', description, "","",post_url,"", extra_infos)  
        
        company_id += 1

def query_disclosures():
    disclosure_url = 'http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/api/disclosures/'
    try:
        response = requests.get(disclosure_url, proxies=proxies, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching disclosures list:", e)
        return

    results = data.get("results", [])
    for disclosure in results:
        company_name = disclosure.get("company_name", "")
        description = disclosure.get("description") or "Not claimed yet"
        file_size = disclosure.get("filesSizes", "")
        post_url = disclosure_url  # fixed endpoint

        extra_infos = {
            'data_size': file_size
        }

        #print(f"Company: {company_name} | Description: {description} | Size: {file_size}")
        appender(company_name, 'silent', description, "", "", post_url, "", extra_infos)




def main():
    json_data = fetch_json_from_onion_url(onion_url)
    if json_data and "companies" in json_data:
        for company in json_data["companies"]:
            # Individually extract all fields
            company_id = company.get("id")
            company_name = company.get("company_name", "").strip()
            country = company.get("country")
            flag = company.get("flag")
            revenue = company.get("revenue")
            employees = company.get("employees")
            all_disclosures = company.get("all_disclosures")
            completed_disclosures = company.get("completed_disclosures")
            iso_date = company.get("date")
            unix_date = company.get("unix_date")
            tag_names = company.get("tag_names", [])
            view_number = company.get("view_number")
            link = company.get("link")
            filters = company.get("filters")

            # Create readable description
            description = (
                f"Country: {country} | "
                f"Revenue: {revenue}M USD | "
                f"Employees: {employees} | "
                f"Tags: {', '.join([tag['name'] for tag in tag_names])}"
            )

            #formatted_timestamp = convert_date(unix_date)
            formatted_timestamp = ""
            extracted = tldextract.extract(link)
            domain = f"{extracted.domain}.{extracted.suffix}"
            #post_url = f"http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion/company/{company_id}"
            post_url = "http://silentbgdghp3zeldwpumnwabglreql7jcffhx5vqkvtf2lshc4n5zid.onion" 

            # Minimal call to appender()
            #appender(post_title, group_name, description="", website="", published="", post_url="", country="")
            appender(company_name, 'silent', description, domain, formatted_timestamp, post_url,country_name_to_code(country))
    query_disclosures()

if __name__ == "__main__":
    main()

