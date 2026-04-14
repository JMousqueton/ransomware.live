#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generic parser template for ransomware.live
Fetches JSON from a leak site
"""

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
URL = "http://cephalus6oiypuwumqlwurvbmwsfglg424zjdmywfgqm4iehkqivsjyd.onion/api/domains"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}


def fetch_data():
    try:
        r = requests.get(URL, proxies=PROXIES, timeout=60)
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
    """
    data = [
            {"domain":"carestlhealth.org","company":"CareSTL Health","logoContent":"CARESTL","description":"CareSTL Health DATA Leak | 500+GB | KAWA4096 STEALED our data","dataLink":"https://darkforums.st/Thread-CareSTL-Health-DATA-Leak-500-GB"},{"domain":"system-exe.co.jp","company":"SystemExec Co., Ltd.","logoContent":"SYSTEM-EXE","description":"SystemExec Co., Ltd. (システムエグゼ) GitLab naked repo leak | 30G+","dataLink":"https://darkforums.st/Thread-Source-Code-SystemExec-Co-Ltd-%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%82%A8%E3%82%B0%E3%82%BC-GitLab-naked-repo-leak-30G"},{"domain":"bararch.com","company":"BAR Architects & Interiors","logoContent":"BARARCH","description":"BAR Architects & Interiors DATA LEAK | 1.5T+","dataLink":"https://darkforums.st/Thread-Document-BAR-Architects-Interiors-DATA-LEAK-1-5T--18961"},{"domain":"kstrategies.com","company":"K Strategies Marketing and Public Relations","logoContent":"KSTRATEGIE","description":"K Strategies Marketing and Public Relations LEAK | 900+GB","dataLink":"https://darkforums.st/Thread-Document-K-Strategies-Marketing-and-Public-Relations-LEAK-900-GB"},{"domain":"balancedsolutions4me.com","company":"LPL Financial","logoContent":"BALANCEDSO","description":"LPL Financial DATA LEAK | (I FORGOT THE SIZE,BUT ITS HUGE)","dataLink":"https://darkforums.st/Thread-Document-LPL-Financial-DATA-LEAK-I-FORGOT-THE-SIZE-BUT-ITS-HUGE"},{"domain":"gmllp.com","company":"Guerrero Mears LLP","logoContent":"GMLLP","description":"Guerrero Mears LLP DATALEAK | (FORGOT THE SIZE)","dataLink":"https://darkforums.st/Thread-Document-Guerrero-Mears-LLP-DATALEAK-FORGOT-THE-SIZE"},{"domain":"sskrplaw.com","company":"Sherman, Silverstein, Kohl, Rose & Podolsky, P.A.","logoContent":"SSKRPLAW","description":"SSKRPLAW DATA LEAK | (5GB+ ZIP)","dataLink":"https://darkforums.st/Thread-Document-SSKRPLAW-DATA-LEAK-5GB-ZIP"},{"domain":"lee-irvine.com","company":"Lee & Associates","logoContent":"LEE-IRVINE","description":"Lee & Associates DATA LEAK | (TB)","dataLink":"https://darkforums.st/Thread-Lee-Associates-DATA-LEAK-TB"},{"domain":"txpregnancy.org","company":"txpregnancy.org - Fake Abortion Clinics Exposed","logoContent":"TXPREGNANC","description":"coming soon","dataLink":""}
]
    """


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
