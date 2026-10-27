from typing import Any

import httpx
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._gateway import ACCOUNT_URL


class ProxmintProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Runs when the key is saved. Reads the account, so it uses no bandwidth.

        A valid key with no product yet is accepted: the tool says which product to buy
        when it is first called.
        """
        api_key = str(credentials.get("api_key") or "").strip()
        try:
            r = httpx.get(ACCOUNT_URL, headers={"Authorization": f"Bearer {api_key}"}, timeout=20)
        except httpx.HTTPError as e:
            raise ToolProviderCredentialValidationError(f"Couldn't reach Proxmint: {e}") from e
        if r.status_code == 401:
            raise ToolProviderCredentialValidationError(
                "Proxmint rejected the API key. Create a new one under Settings in the dashboard."
            )
        if r.status_code != 200:
            raise ToolProviderCredentialValidationError(f"Proxmint answered {r.status_code}. Try again in a minute.")
