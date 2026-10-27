"""Offline checks: a stand-in gateway and account API, no network. Run: pytest tests"""

import sys
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dify_plugin.errors.tool import ToolProviderCredentialValidationError  # noqa: E402

import provider.proxmint as provider_mod  # noqa: E402
import tools.fetch_page as fetch_mod  # noqa: E402
from tools._gateway import Credentials, GatewayError  # noqa: E402

HTML = "<html><head><title>Hi</title><script>x()</script></head><body><h1>Hello</h1><p>world</p></body></html>"


@pytest.fixture
def gateway(monkeypatch):
    """Records each proxy username and account lookup; answers with HTML or a gateway refusal."""
    seen = {"usernames": [], "lookups": 0, "reason": None}
    fetch_mod._logins.clear()

    def load_credentials(api_key, product):
        seen["lookups"] += 1
        assert api_key == "pmk_test"
        return Credentials(f"{product}-login", "pw")

    def client_for(creds, username):
        seen["usernames"].append(username)

        def handler(req):
            if seen["reason"]:
                return httpx.Response(407, extensions={"reason_phrase": seen["reason"].encode()})
            return httpx.Response(200, headers={"content-type": "text/html"}, text=HTML)

        return httpx.Client(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(fetch_mod, "load_credentials", load_credentials)
    monkeypatch.setattr(fetch_mod, "client_for", client_for)
    return seen


def run(**params):
    tool = fetch_mod.FetchPageTool.from_credentials({"api_key": "pmk_test"})
    return list(tool.invoke({"url": "http://example.com/", **params}))


def test_targeting_text_and_metadata(gateway):
    text, meta = run(country="DE", city="München", product="mobile")
    assert gateway["usernames"] == ["mobile-login__cr.de;city.munchen"]
    assert text.message.text == "Hello\n\nworld"
    assert meta.message.json_object == {
        "url": "http://example.com/",
        "status": 200,
        "title": "Hi",
        "content_type": "text/html",
        "truncated": False,
    }


def test_defaults_html_and_cut(gateway):
    text, meta = run(output="html", max_chars="1000.0", country="", city="")
    assert gateway["usernames"] == ["residential-login"]
    assert text.message.text == HTML
    text, meta = run(output="html", max_chars=10)
    assert text.message.text.startswith(HTML[:10] + "\n\n[cut at 10 characters]")
    assert meta.message.json_object["truncated"] is True


def test_login_is_cached_until_the_gateway_refuses(gateway):
    run()
    run()
    assert gateway["lookups"] == 1
    gateway["reason"] = "TRAFFIC_EXHAUSTED"
    with pytest.raises(GatewayError, match="bandwidth is used up"):
        run()
    gateway["reason"] = None
    run()
    assert gateway["lookups"] == 2


def test_city_needs_a_country(gateway):
    with pytest.raises(ValueError, match="need a country"):
        run(city="Paris")


def test_key_validation(monkeypatch):
    answers = iter([httpx.Response(200, json={"products": []}), httpx.Response(401), httpx.Response(503)])
    monkeypatch.setattr(provider_mod.httpx, "get", lambda *a, **k: next(answers))
    p = provider_mod.ProxmintProvider()
    p._validate_credentials({"api_key": "pmk_test"})
    with pytest.raises(ToolProviderCredentialValidationError, match="rejected the API key"):
        p._validate_credentials({"api_key": "pmk_bad"})
    with pytest.raises(ToolProviderCredentialValidationError, match="503"):
        p._validate_credentials({"api_key": "pmk_test"})
