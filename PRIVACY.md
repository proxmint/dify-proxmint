# Privacy policy

This plugin lets Dify read web pages through your own Proxmint proxies.

## Data the plugin handles

- **Your Proxmint API key.** Dify stores it as an encrypted credential in your workspace. The plugin sends it only to
  `https://proxmint.com/api/v1/account`, to read your proxy login. It never logs the key or writes it to disk.
- **Your proxy login.** Read from your account with the key, kept in the plugin's memory for up to 10 minutes, and
  sent only to the proxy gateway `gw.proxmint.com`.
- **The URLs you fetch and the pages they return.** Each request goes through the gateway to the site you asked for,
  and the page comes back to your Dify app.

The plugin does not collect personal data about you or your users, and has no telemetry.

## Storage and retention

Nothing is stored. The plugin has no database, no files and no cache on disk, and the proxy login lives in memory
only. To remove the key, delete the credential in your Dify workspace.

## Third parties

Requests go to Proxmint (`proxmint.com` and `gw.proxmint.com`), then from a proxy exit IP to the site you asked for.
Nothing is sent anywhere else. Proxmint's handling of account and usage data is covered by its privacy policy:
https://proxmint.com/privacy

## Contact

support@proxmint.com
