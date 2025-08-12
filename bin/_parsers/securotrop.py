import requests
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import appender, stdlog, errlog

# --- Your appender function ---
#def appender(victim, group_name, description='', website='', published='', post_url='', country='', extra_infos=[]):
#    print(f"[+] Appended: {victim} ({published}) -> {post_url} | Size: {extra_infos.get('data_size', '')}")

# Tor session setup
session = requests.session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE_URL = "http://securo45z554mw7rgrt7wcgv5eenj2xmxyrsdj3fcjsvindu63s4bsid.onion/"
GROUP_NAME = "securotrop"

# Fields to extract from info.txt
TARGET_FIELDS = {
    "company_name": "Company name",
    "website": "Website",
    "total_size": "Total size",
    "date_of_leak": "Date of leak"
}

def extract_selected_info(text):
    data = {}
    for line in text.strip().splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(" ", "_")
            if key in TARGET_FIELDS:
                data[TARGET_FIELDS[key]] = value.strip()
    return data

def normalize_date(date_str):
    for fmt in ("%Y-%m-%d %H:%M", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d 00:00:00.000000")
        except ValueError:
            continue
    return "INVALID_DATE"

# Main logic
try:
    response = session.get(BASE_URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for row in soup.find_all("tr")[2:-1]:
        cols = row.find_all("td")
        if len(cols) != 5 or cols[0].img['alt'] != "[DIR]":
            continue

        folder = cols[1].a['href']
        name = cols[1].a.text.strip().rstrip('/')
        dir_lastmod = normalize_date(cols[2].text.strip())
        info_url = BASE_URL + folder + "info.txt"
        dir_url = BASE_URL + folder

        # Default values
        data = {
            "Company name": name,
            "Website": "",
            "Total size": "",
            "Date of leak": dir_lastmod,
            "Post URL": dir_url
        }

        try:
            info_resp = session.get(info_url, timeout=10)
            if info_resp.status_code == 200:
                extracted = extract_selected_info(info_resp.text)
                data.update(extracted)
                data["Date of leak"] = normalize_date(data.get("Date of leak", dir_lastmod))
                data["Post URL"] = info_url
        except requests.RequestException:
            pass

        # Append final result
        appender(
            victim=data["Company name"],
            group_name=GROUP_NAME,
            website=data["Website"],
            published=data["Date of leak"],
            post_url=data["Post URL"],
            extra_infos={"data_size": data["Total size"]}
        )

except requests.RequestException as e:
    print(f"[!] Error: {e}")
