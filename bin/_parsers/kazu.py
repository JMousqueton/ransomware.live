#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, json, datetime
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from shared_utils import appender, errlog  # appender will be commented out below

# --- env / paths ---
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

# --- helpers ---
def to_midnight(dt_str: str) -> str:
    """Return 'YYYY-MM-DD 00:00:00.000000' or '' if parse fails."""
    if not dt_str:
        return ""
    dt_str = dt_str.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.datetime.strptime(dt_str, fmt)
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)\
                     .strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            pass
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)\
                 .strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return ""

def js_object_to_json(txt: str) -> str:
    """
    Convert a JS array of plain objects into JSON:
    - Quote unquoted property names
    - Remove trailing commas before ] or }
    DO NOT strip // comments (keeps https:// intact).
    """
    # Quote unquoted keys: { key: value } or , key: value
    txt = re.sub(r'(\{|,)\s*([A-Za-z_]\w*)\s*:',
                 r'\1 "\2":', txt)

    # Remove trailing commas
    txt = re.sub(r',\s*([\]}])', r'\1', txt)
    return txt

def extract_companies_from_js(blob: str):
    """Locate and parse `const companies = [ ... ];` (no fallback)."""
    m = re.search(r'\bconst\s+companies\s*=\s*(\[\s*.*?\s*\]);',
                  blob, re.DOTALL | re.IGNORECASE)
    if not m:
        return []

    arr_js = m.group(1)
    arr_json = js_object_to_json(arr_js)

    try:
        data = json.loads(arr_json)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        # Show a short preview for troubleshooting
        preview = arr_json[:240].replace("\n", "\\n")
        errlog(f"kazu - json_decode_error: {e}; preview: {preview}")
        return []

# --- main ---
def main():
    # group_name from filename (supports symlinked parsers)
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace(".py", "")
    else:
        group_name = os.path.basename(script_path).replace(".py", "")

    emitted = 0

    for filename in os.listdir(tmp_dir):
        if not filename.startswith(group_name + "-"):
            continue

        html_doc = tmp_dir / filename
        raw = html_doc.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "html.parser")

        # Strict: only parse the companies array
        companies = []
        for s in soup.find_all("script"):
            t = s.get_text(separator="\n", strip=False)
            if "const companies" in t:
                companies = extract_companies_from_js(t)
                if companies:
                    break
        if not companies and "const companies" in raw:
            companies = extract_companies_from_js(raw)

        if not companies:
            print(json.dumps({
                "status": "no_items_emitted",
                "group_name": group_name,
                "file": str(filename),
                "reason": "companies array empty or invalid"
            }))
            continue

        for c in companies:
            name = (c.get("name") or "").strip()
            website = (c.get("url") or "").strip()
            description = (c.get("description") or "").strip()
            pubdate = to_midnight(c.get("pubdate") or "")
            ransom = (c.get("ransom") or "").strip()
            size = (c.get("size") or "").strip()

            extra_infos = {
                "data_size": size,
                "ransom": ransom
            }

            # ---- KEEP appender BUT COMMENTED (as requested) ----
            appender(
                 victim=name,
                 group_name=group_name,
                 description=description,
                 website=website,
                 published=str(pubdate),
                 post_url="",
                 country="",
                 extra_infos=extra_infos
             )

if __name__ == "__main__":
    main()
