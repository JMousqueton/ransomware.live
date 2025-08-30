#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests,os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import stdlog, errlog, appender

# Load env
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

# Source URL (à personnaliser selon le parser)
URL = "http://cephalus6oiypuwumqlwurvbmwsfglg424zjdmywfgqm4iehkqivsjyd.onion
API = URL + "/api/domains"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}


def fetch_data():
    try:
        r = requests.get(API, proxies=PROXIES, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        errlog(f"[{GROUP_NAME}] ❌ Error fetching data: {e}")
        return []
        

def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')
    group_name = group_name.replace('-api','')

    data = fetch_data()
    if not data:
        return
   

    for entry in data:
        victim = entry.get("company") or entry.get("domain")
        description = entry.get("description") or ""
        website = entry.get("domain") or ""
        post_url = entry.get("dataLink") or ""

        added = appender(
            victim=victim,
            group_name=group_name,
            description=description,
            website=website,
            published=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            post_url=post_url,
            country="",
            extra_infos=[]
        )

if __name__ == "__main__":
    main()
