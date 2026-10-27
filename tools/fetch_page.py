"""Fetch page: read one web page through the caller's own Proxmint proxy."""

import time
from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._gateway import Credentials, GatewayError, client_for, fetch, load_credentials, proxy_username

# The account lookup is rate limited per IP and Dify Cloud users can share one, so each
# process keeps a key's proxy login for a while instead of asking on every call.
LOGIN_TTL = 600.0
_logins: dict[tuple[str, str], tuple[float, Credentials]] = {}


def login(api_key: str, product: str) -> Credentials:
    hit = _logins.get((api_key, product))
    if hit and hit[0] > time.monotonic():
        return hit[1]
    creds = load_credentials(api_key, product)
    _logins[(api_key, product)] = (time.monotonic() + LOGIN_TTL, creds)
    return creds


class FetchPageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = str(self.runtime.credentials.get("api_key") or "").strip()
        product = tool_parameters.get("product") or "residential"
        max_chars = int(float(tool_parameters.get("max_chars") or 50_000))
        try:
            creds = login(api_key, product)
            username = proxy_username(
                creds.username,
                country=(tool_parameters.get("country") or "").strip() or None,
                city=(tool_parameters.get("city") or "").strip() or None,
            )
            with client_for(creds, username) as client:
                page = fetch(client, str(tool_parameters.get("url") or "").strip())
        except GatewayError:
            _logins.pop((api_key, product), None)  # a changed login or a used-up product shows up here first
            raise
        except httpx.HTTPError as e:
            raise RuntimeError(f"Request failed: {e}") from e

        body = page.html if tool_parameters.get("output") == "html" else page.text()
        truncated = len(body) > max_chars
        if truncated:
            body = body[:max_chars] + f"\n\n[cut at {max_chars:,} characters]"
        yield self.create_text_message(body)
        yield self.create_json_message(
            {
                "url": page.url,
                "status": page.status,
                "title": page.title,
                "content_type": page.content_type,
                "truncated": truncated,
            }
        )
