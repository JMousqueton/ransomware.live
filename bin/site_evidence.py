"""Country evidence from a victim's own public homepage.

Deterministic and model-free: structured address data (schema.org JSON-LD), the
country of valid phone numbers, the page locale, and the page title/meta text.
Only static HTML is parsed, nothing is executed.

The fetch is hardened because the site belongs to a breached company that may be
compromised or hostile: public IPs only (re-checked on every redirect), a few
redirects, a short timeout, a size cap and HTML content types only. Evidence is
discarded when the page does not look like the victim (name/domain mismatch),
because the domain itself is often an AI guess.
"""
import ipaddress
import json
import logging
import re
import socket
import time
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests
import tldextract

log = logging.getLogger(__name__)

_extract = tldextract.TLDExtract(suffix_list_urls=())

MAX_BYTES = 512 * 1024
MAX_REDIRECTS = 3
TIMEOUT = (4, 6)
DEADLINE = 12  # hard cap in seconds for the whole fetch; slow-drip servers must not stall us
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ransomware.live country check)",
           "Accept": "text/html,application/xhtml+xml"}


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''
        self.meta = {}
        self.lang = ''
        self.jsonld = []
        self.tels = []
        self._in_title = False
        self._in_ld = False
        self._ld = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang') or ''
        elif tag == 'title':
            self._in_title = True
        elif tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            if key and a.get('content'):
                self.meta[key] = a['content']
        elif tag == 'script' and (a.get('type') or '').lower() == 'application/ld+json':
            self._in_ld, self._ld = True, []
        elif tag == 'a' and (a.get('href') or '').lower().startswith('tel:'):
            self.tels.append(a['href'][4:])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        elif tag == 'script' and self._in_ld:
            self._in_ld = False
            try:
                self.jsonld.append(json.loads(''.join(self._ld)))
            except ValueError:
                pass

    def handle_data(self, data):
        if self._in_title and len(self.title) < 300:
            self.title += data
        elif self._in_ld:
            self._ld.append(data)


def _public_host(host):
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False
    return bool(infos) and all(ipaddress.ip_address(i[4][0]).is_global for i in infos)


def fetch_html(website):
    """Return the homepage HTML (capped) or '' on any failure, policy refusal or deadline."""
    host = re.sub(r'^[a-z]+://', '', (website or '').strip().lower()).split('/')[0]
    if not host or '*' in host:
        return ''
    deadline = time.monotonic() + DEADLINE
    for scheme in ('https', 'http'):
        url = f'{scheme}://{host}/'
        try:
            for _ in range(MAX_REDIRECTS + 1):
                if time.monotonic() > deadline:
                    return ''
                parsed = urlparse(url)
                if parsed.scheme not in ('http', 'https') or not _public_host(parsed.hostname or ''):
                    return ''
                r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True,
                                 allow_redirects=False)
                if r.is_redirect or r.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, r.headers.get('Location', ''))
                    r.close()
                    continue
                if r.status_code != 200 or 'html' not in r.headers.get('Content-Type', '').lower():
                    r.close()
                    break
                body = b''
                for chunk in r.iter_content(chunk_size=16384):
                    body += chunk
                    if len(body) >= MAX_BYTES or time.monotonic() > deadline:
                        break
                r.close()
                return body[:MAX_BYTES].decode(r.encoding or 'utf-8', errors='replace')
        except requests.RequestException as e:
            log.info('site evidence: %s unreachable (%s)', url, e)
    return ''


def _looks_like_victim(victim, website, title):
    squash = re.sub(r'[^a-z0-9]', '', victim.lower())
    label = _extract(website or '').domain.lower()
    if label and squash and (label in squash or squash in label):
        return True
    text = (title or '').lower()
    return any(len(t) >= 4 and t in text for t in re.findall(r'[a-z0-9]+', victim.lower()))


def _country_from_value(value, to_code):
    if isinstance(value, dict):
        value = value.get('name') or value.get('@id')
    return to_code(value) if isinstance(value, str) else ''


def _jsonld_countries(node, to_code, out):
    if isinstance(node, list):
        for n in node:
            _jsonld_countries(n, to_code, out)
    elif isinstance(node, dict):
        if 'addressCountry' in node:
            code = _country_from_value(node['addressCountry'], to_code)
            if code:
                out.append(code)
        for v in node.values():
            if isinstance(v, (dict, list)):
                _jsonld_countries(v, to_code, out)


def _unique(codes):
    return codes[0] if codes and len(set(codes)) == 1 else ''


def _phone_country(numbers):
    try:
        import phonenumbers
    except ImportError:
        return ''
    regions = []
    for raw in numbers:
        try:
            num = phonenumbers.parse(raw.strip(), None)  # international (+CC) numbers only
        except phonenumbers.NumberParseException:
            continue
        if phonenumbers.is_valid_number(num):
            region = phonenumbers.region_code_for_number(num)
            if region:
                regions.append(region)
    if not regions:
        return ''
    top, n = Counter(regions).most_common(1)[0]
    return top if n * 2 > len(regions) else ''


def extract_evidence(html_text, victim, website, to_code, description_country):
    """Pure parser: HTML -> evidence dict. to_code maps a country name/code to alpha-2."""
    page = _Page()
    try:
        page.feed(html_text)
    except Exception:  # malformed markup must never break resolution
        pass
    title = re.sub(r'\s+', ' ', page.title).strip()
    if not _looks_like_victim(victim, website, title):
        return {}
    meta = page.meta.get('description') or page.meta.get('og:description') or ''

    jsonld = []
    _jsonld_countries(page.jsonld, to_code, jsonld)

    locale = page.meta.get('og:locale') or page.lang
    # English locales (en_US, en_GB...) are the CMS default on sites worldwide: no signal.
    m = re.match(r'^([a-z]{2,3})[-_]([A-Za-z]{2})$', locale.strip())
    locale_country = to_code(m.group(2)) if m and m.group(1).lower() != 'en' else ''

    phone_text = re.findall(r'\+\d[\d\s().\-]{7,18}\d', html_text[:200_000])
    return {
        'title': title,
        'meta': re.sub(r'\s+', ' ', meta).strip()[:300],
        'jsonld': _unique(jsonld),
        'phone': _phone_country(page.tels + phone_text),
        'locale': locale_country,
        'text': description_country(f'{title}. {meta}'),
    }


def site_evidence(victim, website, to_code, description_country):
    html_text = fetch_html(website)
    return extract_evidence(html_text, victim, website, to_code, description_country) if html_text else {}
