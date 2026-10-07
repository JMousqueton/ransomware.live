import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
from country_resolver import description_country, resolve_country, tld_country, to_code
from site_evidence import extract_evidence


def fake_llm(country, confidence="high"):
    return lambda *args: {"country": country, "confidence": confidence}


@pytest.mark.parametrize("site,expected", [
    ("www.octomeca.fi", "FI"),
    ("https://www.bbc.co.uk/news", "GB"),
    ("example.com.co", "CO"),
    ("example.co", ""),
    ("startup.io", ""),
    ("deltamarine.com", ""),
    ("agency.gov", "US"),
    ("site.eu", ""),
    ("", ""),
])
def test_tld_country(site, expected):
    assert tld_country(site) == expected


@pytest.mark.parametrize("text,expected", [
    ("Country: Finland", "FI"),
    ("Finland", "FI"),
    ("Delta Marine is a Seattle-based yacht builder in Seattle, Washington, United States", ""),
    ("Philadelphia-based architectural firm headquartered in Philadelphia, United States", "US"),
    ("Kilpi-Koskinen Oy is a Finnish family-owned company founded in 1985", "FI"),
    ("ZEF, Germany - Center for Development Research", ""),
    ("A global supplier with offices in Germany and Finland", ""),
    ("Finnish company with a Swedish subsidiary", "FI"),
    ("Guatemalan IT systems integrator", ""),
    ("N/A", ""),
    ("an engineering consultancy based in Monroe Township, New Jersey", ""),
    ("a firm based in Albuquerque, New Mexico", ""),
    ("a manufacturer based in Auckland, New Zealand", "NZ"),
])
def test_description_country(text, expected):
    assert description_country(text) == expected


def test_delta_marine_not_swapped_for_deltamarin():
    # Bare generic TLD, no description: only the LLM can decide.
    code, _ = resolve_country("Delta Marine", "N/A", "www.deltamarine.com", llm=fake_llm("US"))
    assert code == "US"


def test_llm_not_called_when_tld_decides():
    def boom(*a):
        raise AssertionError("LLM should not be called")
    assert resolve_country("Acme", "", "acme.de", llm=boom)[0] == "DE"


def test_conflicting_signals_go_to_llm_as_tiebreak():
    # ccTLD says DE, the description says Finnish: signals tie, the model breaks it.
    code, _ = resolve_country("Acme", "Acme is a Finnish company", "acme.de", llm=fake_llm("FI"))
    assert code == "FI"
    assert resolve_country("Acme", "Acme is a Finnish company", "acme.de", llm=fake_llm("FI", "medium"))[0] == ""


def test_llm_not_called_when_description_decides():
    def boom(*a):
        raise AssertionError("LLM should not be called")
    assert resolve_country("Acme", "Acme is a Finnish company", "acme.com", llm=boom)[0] == "FI"


def test_medium_needs_corroboration():
    assert resolve_country("Acme", "", "acme.com", llm=fake_llm("US", "medium"))[0] == ""
    assert resolve_country("Acme", "", "acme.us", llm=fake_llm("US", "medium"))[0] == "US"


def test_low_confidence_is_empty():
    assert resolve_country("Acme", "", "acme.com", llm=fake_llm("US", "low"))[0] == ""


def test_ai_description_is_not_independent_evidence():
    # The AI description says Finnish; it must not override the LLM verdict as a "decisive" signal.
    code, _ = resolve_country("Acme", "Acme is a Finnish company", "acme.com",
                              description_is_ai=True, llm=fake_llm("US"))
    assert code == "US"


def test_tld_and_description_agree_skips_llm():
    def boom(*a):
        raise AssertionError("LLM should not be called")
    code, _ = resolve_country("Octomeca", "Octomeca is a Finnish company", "octomeca.fi", llm=boom)
    assert code == "FI"


def test_parser_country_trusted_but_conflict_with_tld_is_empty():
    assert resolve_country("X", "", "x.com", parser_country="se")[0] == "SE"
    assert resolve_country("X", "", "x.fi", parser_country="SE")[0] == ""


def test_llm_failure_falls_back_to_tld():
    def broken(*a):
        raise RuntimeError("quota")
    assert resolve_country("X", "", "x.fi", llm=broken)[0] == "FI"
    assert resolve_country("X", "", "x.com", llm=broken)[0] == ""


def test_masked_victim_never_calls_llm():
    def boom(*a):
        raise AssertionError("LLM should not be called")
    assert resolve_country("***m*sic.fi", "", "***m*sic.fi", llm=boom)[0] == "FI"


def test_invalid_llm_code_ignored():
    assert resolve_country("X", "", "x.com", llm=fake_llm("ZZ"))[0] == ""


SEATTLE_PAGE = """<html lang="en-US"><head><title>Delta Marine Industries | Yacht Builder</title>
<meta name="description" content="Delta Marine is a Seattle-based builder of luxury yachts.">
<script type="application/ld+json">{"@type":"Organization","address":
{"@type":"PostalAddress","addressLocality":"Seattle","addressCountry":"US"}}</script>
</head><body><a href="tel:+12065551234">call</a></body></html>"""


def test_extract_evidence_from_homepage():
    ev = extract_evidence(SEATTLE_PAGE, "Delta Marine", "deltamarine.com", to_code, description_country)
    assert ev["jsonld"] == "US" and ev["locale"] == "" and ev["text"] == ""  # en-US is no signal
    assert ev["title"].startswith("Delta Marine")


def test_homepage_of_a_different_company_is_discarded():
    page = "<html><head><title>Totally Unrelated Corp</title></head></html>"
    assert extract_evidence(page, "Delta Marine", "wrongsite.com", to_code, description_country) == {}


def test_homepage_evidence_overrides_a_model_that_picks_the_wrong_company():
    # Weak/wrong model says FI (the Deltamarin mix-up); the site's own address says US.
    site = lambda victim, website: {"jsonld": "US", "locale": "US"}
    code, why = resolve_country("Delta Marine", "N/A", "deltamarine.com",
                                llm=fake_llm("FI", "high"), site=site)
    assert code == "US", why


def test_models_cannot_override_decided_signals():
    site = lambda victim, website: {"jsonld": "DE"}
    assert resolve_country("Acme", "", "acme.de", llm=fake_llm("FI"), site=site)[0] == "DE"


def test_site_not_fetched_when_cheap_signals_decide():
    def boom(*a):
        raise AssertionError("site should not be fetched")
    assert resolve_country("Acme", "", "acme.fi", site=boom)[0] == "FI"


def test_site_only_signals_need_enough_weight():
    assert resolve_country("Acme", "", "acme.com", site=lambda v, w: {"locale": "US"})[0] == ""
    assert resolve_country("Acme", "", "acme.com", site=lambda v, w: {"phone": "US", "locale": "US"})[0] == "US"


def test_site_failure_degrades_gracefully():
    def boom(*a):
        raise RuntimeError("timeout")
    assert resolve_country("X", "", "x.fi", site=boom)[0] == "FI"


def test_non_english_locale_counts():
    page = '<html lang="fi-FI"><head><title>Acme Oy</title></head></html>'
    assert extract_evidence(page, "Acme", "acme.com", to_code, description_country)["locale"] == "FI"


# --- provider selection -----------------------------------------------------

import country_resolver


@pytest.fixture
def clean_env(monkeypatch):
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "COUNTRY_PROVIDER", "COUNTRY_MODEL", "OPENAI_MODEL"):
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


def fake_providers(monkeypatch, calls):
    def make(name):
        return (lambda prompt, model: calls.append((name, model)) or '{"country": "FI", "confidence": "high"}',
                f"{name.upper()}_API_KEY", {"anthropic": lambda: "claude-x", "openai": lambda: "gpt-x"}[name])
    monkeypatch.setattr(country_resolver, "PROVIDERS", {n: make(n) for n in ("anthropic", "openai")})


def test_no_provider_without_keys(clean_env):
    assert country_resolver.pick_provider() == ""
    assert country_resolver.ask_llm("X", "x.com", "", "", False) == {}


def test_openai_only_is_used(clean_env):
    calls = []
    fake_providers(clean_env, calls)
    clean_env.setenv("OPENAI_API_KEY", "k")
    assert country_resolver.ask_llm("X", "x.com", "", "", False)["country"] == "FI"
    assert calls == [("openai", "gpt-x")]


def test_anthropic_preferred_when_both_set_and_provider_can_be_forced(clean_env):
    calls = []
    fake_providers(clean_env, calls)
    clean_env.setenv("ANTHROPIC_API_KEY", "k")
    clean_env.setenv("OPENAI_API_KEY", "k")
    country_resolver.ask_llm("X", "x.com", "", "", False)
    clean_env.setenv("COUNTRY_PROVIDER", "openai")
    country_resolver.ask_llm("X", "x.com", "", "", False)
    assert [c[0] for c in calls] == ["anthropic", "openai"]


def test_forced_provider_without_key_disables_llm(clean_env):
    clean_env.setenv("OPENAI_API_KEY", "k")
    clean_env.setenv("COUNTRY_PROVIDER", "anthropic")
    assert country_resolver.pick_provider() == ""


def test_country_model_override(clean_env):
    calls = []
    fake_providers(clean_env, calls)
    clean_env.setenv("OPENAI_API_KEY", "k")
    clean_env.setenv("COUNTRY_MODEL", "my-model")
    country_resolver.ask_llm("X", "x.com", "", "", False)
    assert calls == [("openai", "my-model")]
