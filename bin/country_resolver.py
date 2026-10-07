"""Victim country resolution.

Every signal is a weighted vote for a country; the LLM is just one voter, so the
result does not hinge on which model the operator runs. Signals: parser data,
domain ccTLD, a country the description explicitly states, and evidence from the
victim's own homepage (structured address, phone country, locale, page text).
A country is only returned when it clears a minimum score AND leads the runner-up
clearly; conflicting or weak evidence yields an empty country, because a missing
country is better than a wrong one in the site's filter.

Kept free of heavy imports so it can be tested without the rest of the stack.
"""
import json
import logging
import os
import re
from collections import defaultdict

import pycountry
import tldextract

log = logging.getLogger(__name__)

# Offline: use the bundled public suffix snapshot, never hit the network.
_extract = tldextract.TLDExtract(suffix_list_urls=())

DEFAULT_MODEL = "claude-sonnet-4-6"  # override with COUNTRY_MODEL

# ccTLDs that are marketed generically; they say nothing about the owner's country.
BORROWED_TLDS = {
    'ac', 'ai', 'cc', 'co', 'fm', 'gg', 'gl', 'io', 'im', 'la', 'ly', 'me',
    'nu', 'sh', 'tk', 'to', 'tv', 'vc', 'ws', 'cx', 'ms', 'so', 'su',
}
# Non-ccTLD suffixes that are restricted to one country.
US_ONLY_TLDS = {'gov', 'mil', 'edu'}

DEMONYMS = {
    'American': 'US', 'Argentine': 'AR', 'Argentinian': 'AR', 'Australian': 'AU',
    'Austrian': 'AT', 'Belgian': 'BE', 'Brazilian': 'BR', 'British': 'GB',
    'Bulgarian': 'BG', 'Canadian': 'CA', 'Chilean': 'CL', 'Chinese': 'CN',
    'Colombian': 'CO', 'Croatian': 'HR', 'Czech': 'CZ', 'Danish': 'DK',
    'Dutch': 'NL', 'Egyptian': 'EG', 'Estonian': 'EE', 'Finnish': 'FI',
    'French': 'FR', 'German': 'DE', 'Greek': 'GR', 'Hungarian': 'HU',
    'Icelandic': 'IS', 'Indian': 'IN', 'Indonesian': 'ID', 'Irish': 'IE',
    'Israeli': 'IL', 'Italian': 'IT', 'Japanese': 'JP', 'Kenyan': 'KE',
    'Korean': 'KR', 'Kuwaiti': 'KW', 'Latvian': 'LV', 'Lithuanian': 'LT',
    'Malaysian': 'MY', 'Mexican': 'MX', 'Moroccan': 'MA', 'Nigerian': 'NG',
    'Norwegian': 'NO', 'Pakistani': 'PK', 'Peruvian': 'PE', 'Philippine': 'PH',
    'Polish': 'PL', 'Portuguese': 'PT', 'Romanian': 'RO', 'Russian': 'RU',
    'Saudi': 'SA', 'Serbian': 'RS', 'Singaporean': 'SG', 'Slovak': 'SK',
    'Slovenian': 'SI', 'Spanish': 'ES', 'Swedish': 'SE', 'Swiss': 'CH',
    'Taiwanese': 'TW', 'Thai': 'TH', 'Turkish': 'TR', 'Ukrainian': 'UA',
    'Emirati': 'AE', 'Vietnamese': 'VN',
}

# Country names that are also ordinary words / US states / given names.
AMBIGUOUS_NAMES = {'Georgia', 'Jordan', 'Chad', 'Niger', 'Guinea', 'Turkey', 'Mali'}

# Common names pycountry stores under a different official name.
NAME_ALIASES = {
    'USA': 'US', 'U.S.': 'US', 'UK': 'GB', 'U.K.': 'GB', 'England': 'GB',
    'Scotland': 'GB', 'Wales': 'GB', 'Great Britain': 'GB', 'UAE': 'AE',
    'South Korea': 'KR', 'Russia': 'RU', 'Vietnam': 'VN', 'Czech Republic': 'CZ',
    'Czechia': 'CZ', 'Turkiye': 'TR', 'Türkiye': 'TR', 'Taiwan': 'TW',
    'Netherlands': 'NL', 'The Netherlands': 'NL', 'Iran': 'IR', 'Syria': 'SY',
}

_COMPANY_WORDS = (
    r'(?:company|firm|group|provider|manufacturer|organi[sz]ation|institute|'
    r'university|college|hospital|municipality|city|agency|supplier|business|'
    r'corporation|studio|retailer|bank|school|clinic)'
)


def _build_name_map():
    names = dict(NAME_ALIASES)
    for c in pycountry.countries:
        names[c.name] = c.alpha_2
        common = getattr(c, 'common_name', None)
        if common:
            names[common] = c.alpha_2
    # "Korea, Republic of"-style official names are not how descriptions read.
    return {n: code for n, code in names.items() if ',' not in n and n not in AMBIGUOUS_NAMES}


_NAME_MAP = _build_name_map()
# (?<!New ) so "New Jersey" / "New Mexico" are not read as Jersey / Mexico.
_NAME_ALT = '(?<!New )(?:' + '|'.join(
    sorted((re.escape(n) for n in _NAME_MAP), key=len, reverse=True)) + ')'
_DEMONYM_ALT = '|'.join(sorted(DEMONYMS, key=len, reverse=True))

_PATTERNS = [
    # "Country: Finland"
    re.compile(rf'^\s*Country\s*:\s*(?P<c>{_NAME_ALT})\b'),
    # "based in Seattle, Washington, United States" / "headquartered in Finland"
    re.compile(
        r'\b(?:based|headquartered|located|situated|founded|established|registered)\s+in\s+'
        rf"(?:[A-Z][\w'.\-]*,?\s+){{0,3}}?(?P<c>{_NAME_ALT})\b"
    ),
    # "Finland-based"
    re.compile(rf'\b(?P<c>{_NAME_ALT})-based\b'),
    # "a Finnish family-owned company"
    re.compile(rf'\b(?P<d>{_DEMONYM_ALT})\s+(?:[\w\-]+\s+){{0,2}}{_COMPANY_WORDS}\b', re.I),
    # whole description is just the country ("Finland")
    re.compile(rf'^\s*(?P<c>{_NAME_ALT})\s*\.?\s*$'),
]


def valid_code(code):
    """Return the upper-cased alpha-2 code if it is a real ISO 3166-1 country, else ''."""
    if not isinstance(code, str) or len(code.strip()) != 2:
        return ''
    code = code.strip().upper()
    return code if pycountry.countries.get(alpha_2=code) else ''


def tld_country(website):
    """Country implied by the domain's ccTLD, or '' for generic/borrowed TLDs."""
    if not website:
        return ''
    host = re.sub(r'^[a-z]+://', '', website.strip().lower()).split('/')[0]
    ext = _extract(host)
    suffix = ext.suffix
    if not suffix:
        return ''
    labels = suffix.split('.')
    last = labels[-1]
    if last in US_ONLY_TLDS:
        return 'US'
    if len(last) != 2:
        return ''
    if last in BORROWED_TLDS and len(labels) == 1:
        return ''  # "example.co" is generic, "example.com.co" is Colombian
    if last == 'uk':
        return 'GB'
    if last == 'eu':
        return ''
    return valid_code(last)


def description_country(description):
    """Country the description explicitly states the company is from, or ''.

    Only decisive phrasings count ("based in X", "X-based", "Country: X", a
    demonym attached to a company noun). Passing mentions of a country do not,
    and conflicting statements yield nothing.
    """
    if not description:
        return ''
    found = set()
    for pat in _PATTERNS:
        for m in pat.finditer(description):
            groups = m.groupdict()
            if groups.get('c') and groups['c'] in _NAME_MAP:
                found.add(_NAME_MAP[groups['c']])
            elif groups.get('d'):
                demonym = next((d for d in DEMONYMS if d.lower() == groups['d'].lower()), None)
                if demonym:
                    found.add(DEMONYMS[demonym])
    return found.pop() if len(found) == 1 else ''


WEIGHTS = {
    'parser': 4, 'tld': 3, 'description': 3,
    'jsonld': 4, 'phone': 2, 'site-text': 2, 'locale': 1,
    'llm-high': 3, 'llm-medium': 1,
}
MIN_SCORE = 3     # a lone strong signal (ccTLD, stated country, high-confidence LLM) is enough
MARGIN = 2        # ...but it must beat the runner-up by this much
# Order: cheap signals -> homepage evidence -> LLM. Each stage runs only if the
# previous ones could not decide, so the model is a last resort, never an override.


def _build_prompt(victim, website, tld, description, description_is_ai, facts=None):
    facts = facts or {}
    lines = [
        "A ransomware group listed a victim. Determine the country where this company "
        "is headquartered.",
        "",
        f'Victim name on the leak site: "{victim}"',
        f"Domain: {website or 'unknown'}",
    ]
    if tld:
        lines.append(f"Domain country-code TLD points to: {tld}")
    if facts.get('title') or facts.get('meta'):
        lines.append(f"Homepage title: {facts.get('title', '')}")
        lines.append(f"Homepage description: {facts.get('meta', '')}")
    for key, label in (('jsonld', 'Homepage structured address country'),
                       ('phone', 'Country of phone numbers on the homepage'),
                       ('locale', 'Homepage locale country')):
        if facts.get(key):
            lines.append(f"{label}: {facts[key]}")
    if description:
        source = ("generated earlier by an AI, may be wrong" if description_is_ai
                  else "from the leak site or a data broker")
        lines.append(f"Description ({source}): {description}")
    lines += [
        "",
        "Rules:",
        "- Many company names are shared by unrelated firms in different countries. "
        "Identify the company by its domain, homepage and description first, and never "
        "substitute a similarly named or better-known company in another country.",
        "- If the evidence is ambiguous or you do not know this company, answer null.",
        "- Answer only with a JSON object: "
        '{"country": "<ISO 3166-1 alpha-2 or null>", '
        '"confidence": "high|medium|low", "reason": "<one short sentence>"}',
        "- Use \"high\" only when you are certain which company this is and where it is based.",
    ]
    return "\n".join(lines)


def _parse_llm_json(text):
    m = re.search(r'\{.*\}', text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except ValueError:
        return {}


def _complete_anthropic(prompt, model):
    import anthropic  # lazy: keeps the pure helpers importable without the SDK
    completion = anthropic.Anthropic().messages.create(  # key from ANTHROPIC_API_KEY
        model=model, max_tokens=1024, messages=[{"role": "user", "content": prompt}])
    # Newer models may lead with a thinking block; take the first text block.
    return next((b.text for b in completion.content if getattr(b, 'type', '') == 'text'), '')


def _complete_openai(prompt, model):
    from openai import OpenAI  # lazy; key from OPENAI_API_KEY
    completion = OpenAI().chat.completions.create(
        model=model, max_completion_tokens=1024, messages=[{"role": "user", "content": prompt}])
    return completion.choices[0].message.content or ''


# provider -> (completion function, API key env var, default model)
PROVIDERS = {
    'anthropic': (_complete_anthropic, 'ANTHROPIC_API_KEY', lambda: DEFAULT_MODEL),
    'openai': (_complete_openai, 'OPENAI_API_KEY', lambda: os.getenv('OPENAI_MODEL') or 'gpt-4o'),
}


def pick_provider():
    """COUNTRY_PROVIDER if set, else the first provider with an API key configured, else ''."""
    forced = (os.getenv('COUNTRY_PROVIDER') or '').lower()
    if forced:
        return forced if forced in PROVIDERS and os.getenv(PROVIDERS[forced][1]) else ''
    return next((name for name, (_, env, _) in PROVIDERS.items() if os.getenv(env)), '')


def ask_llm(victim, website, tld, description, description_is_ai, facts=None):
    """One combined LLM call on the configured provider.

    Returns {'country', 'confidence', 'reason'}, or {} if no provider is configured.
    The model comes from COUNTRY_MODEL, else the provider's default (OPENAI_MODEL for OpenAI).
    """
    provider = pick_provider()
    if not provider:
        return {}
    complete, _, default_model = PROVIDERS[provider]
    model = os.getenv('COUNTRY_MODEL') or default_model()
    prompt = _build_prompt(victim, website, tld, description, description_is_ai, facts)
    return _parse_llm_json(complete(prompt, model))


def to_code(value):
    """Country name or alpha-2 code -> alpha-2 ('' if unrecognised)."""
    if not isinstance(value, str) or not value.strip():
        return ''
    value = value.strip()
    if len(value) == 2:
        return valid_code(value)
    if value in _NAME_MAP:
        return _NAME_MAP[value]
    try:
        return pycountry.countries.lookup(value).alpha_2
    except LookupError:
        return ''


def _decide(votes):
    """votes: [(code, source)] -> (code or '', score, reason)."""
    scores = defaultdict(int)
    for code, source in votes:
        scores[code] += WEIGHTS[source]
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    summary = ', '.join(f'{c}:{s}' for c, s in ranked) or 'no signals'
    if not ranked:
        return '', 0, 'no signals'
    top, score = ranked[0]
    runner = ranked[1][1] if len(ranked) > 1 else 0
    if score >= MIN_SCORE and score - runner >= MARGIN:
        return top, score, f'votes {summary} [{", ".join(s for c, s in votes if c == top)}]'
    return '', score, f'inconclusive: votes {summary}'


def resolve_country(victim, description='', website='', parser_country='',
                    description_is_ai=False, llm=None, site=None):
    """Return (country_code_or_empty, reason).

    llm:  callable(victim, website, tld, description, description_is_ai, facts) -> dict
    site: callable(victim, website) -> evidence dict from the victim's homepage
    Either may be None to resolve from the remaining signals only.
    """
    description = '' if (description or '').strip().upper() in ('', 'N/A') else description
    tld = tld_country(website)
    votes = []
    if valid_code(parser_country):
        votes.append((valid_code(parser_country), 'parser'))
    if tld:
        votes.append((tld, 'tld'))
    if not description_is_ai and description_country(description):
        votes.append((description_country(description), 'description'))

    code, _, why = _decide(votes)
    if code:
        return code, why

    facts = {}
    if site is not None and '*' not in victim:
        try:
            facts = site(victim, website) or {}
        except Exception as e:
            log.warning('country: site evidence failed for "%s": %s', victim, e)
        for key, source in (('jsonld', 'jsonld'), ('phone', 'phone'),
                            ('text', 'site-text'), ('locale', 'locale')):
            if valid_code(facts.get(key)):
                votes.append((facts[key], source))
        code, _, why = _decide(votes)
        if code:
            return code, why

    # Signals alone could not decide: only now ask the model, as one more vote.

    if llm is not None and '*' not in victim:
        try:
            answer = llm(victim, website, tld, description, description_is_ai, facts) or {}
        except Exception as e:  # network, quota, malformed response: degrade, don't crash
            log.warning('country: LLM lookup failed for "%s": %s', victim, e)
            answer = {}
        confidence = str(answer.get('confidence', '')).lower()
        if valid_code(answer.get('country')) and confidence in ('high', 'medium'):
            votes.append((valid_code(answer['country']), f'llm-{confidence}'))

    code, _, why = _decide(votes)
    return code, why


def fetch_site_evidence(victim, website):
    """Default `site` callable. Disable with COUNTRY_FETCH_SITE=0."""
    if os.getenv('COUNTRY_FETCH_SITE', '1') == '0' or not website:
        return {}
    import site_evidence  # lazy: pulls in requests
    return site_evidence.site_evidence(victim, website, to_code, description_country)
