#!/usr/bin/env python3
"""List victims whose stored country contradicts the deterministic signals.

Reads victims from the public API (or a local JSON dump) and reports rows where
the stored country disagrees with the domain's ccTLD or with a country the
description explicitly states. No LLM involved; add --llm to also re-ask the
resolver for the flagged rows (needs ANTHROPIC_API_KEY or OPENAI_API_KEY).

    audit_countries.py --country FI
    audit_countries.py --file victims.json
"""
import argparse
import json
import os
import sys
import urllib.request

from country_resolver import ask_llm, description_country, fetch_site_evidence, pick_provider, resolve_country, tld_country, valid_code

API = "https://api.ransomware.live/v2"


def load(args):
    if args.file:
        with open(args.file, encoding='utf-8') as f:
            return json.load(f)
    url = f"{API}/countryvictims/{args.country}" if args.country else f"{API}/recentvictims"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('--country', help='ISO alpha-2 code, fetch that country from the API')
    ap.add_argument('--file', help='local JSON dump instead of the API')
    ap.add_argument('--llm', action='store_true', help='re-resolve flagged rows with the LLM')
    args = ap.parse_args()

    llm = None
    if args.llm:
        if not pick_provider():
            sys.exit('no LLM configured: set ANTHROPIC_API_KEY or OPENAI_API_KEY')
        llm = ask_llm

    rows = load(args)
    flagged = 0
    for r in rows:
        name = r.get('victim') or r.get('post_title', '')
        site = r.get('domain') or r.get('website', '')
        desc = r.get('description') or ''
        stored = valid_code(r.get('country'))
        if not stored:
            continue
        is_ai = desc.startswith('[AI generated]')
        tld = tld_country(site)
        said = '' if is_ai else description_country(desc)
        problems = []
        if tld and tld != stored:
            problems.append(f'tld={tld}')
        if said and said != stored:
            problems.append(f'description={said}')
        if not problems:
            continue
        flagged += 1
        line = f'{name[:38]:<39} stored={stored} {" ".join(problems):<28} {site}'
        if llm:
            code, why = resolve_country(name, desc, site, description_is_ai=is_ai, llm=llm,
                                        site=fetch_site_evidence)
            line += f'  -> {code or "(empty)"} [{why}]'
        print(line)
    print(f'\n{flagged} of {len(rows)} rows flagged', file=sys.stderr)


if __name__ == '__main__':
    main()
