# Proxmint

Read web pages through [Proxmint](https://proxmint.com) residential, datacenter or 4G/5G mobile proxies from a Dify
agent, chatflow or workflow. Pick the exit country and city per call, and get the page back as readable text or raw
HTML.

Use it for pages that block cloud servers, or that show different prices, results or content in different countries.

## Tool

**Fetch page** reads one URL and returns:

- `text`: the page as readable text (scripts and styles removed), or the raw HTML
- `json`: the final URL after redirects, the HTTP status, the page title, the content type, and whether the text was cut

| Parameter | Set by | What it does |
| --- | --- | --- |
| URL | model or you | The http or https page to read |
| Country | model or you | Two-letter code for the exit IP, for example `us` or `de`. Empty means any country |
| City | model or you | City for the exit IP, for example `New York`. Needs a country |
| Proxy product | you | Residential, premium residential, datacenter or mobile |
| Output | you | Readable text or raw HTML |
| Max characters | you | Longer pages are cut. Default 50,000 |

Every call gets a new exit IP.

## Setup

1. Create a Proxmint account and buy bandwidth for at least one product on the
   [pricing page](https://proxmint.com/pricing). Bandwidth is sold per GB with no subscription, and can be
   [paid in crypto](https://proxmint.com/buy-proxies-with-crypto).
2. Create an API key under **Settings** in the [dashboard](https://proxmint.com/dashboard/settings).
3. In Dify, install **Proxmint**, open **Tools > Proxmint > Authorize** and paste the key. Saving it reads your
   account and uses no bandwidth.
4. Add **Fetch page** to an agent, or as a tool node in a workflow.

## Usage

In an agent, ask for something that needs the live page, for example *"What does the front page of example.com say
when visited from Germany?"*. The model fills in the URL and the country.

In a workflow, set the URL from an earlier node and read `text` for the page, or `json` for the status and title.

## Credentials

The plugin needs one Proxmint API key (`pmk_...`). It uses the key to read the proxy login of the product you choose
from `https://proxmint.com/api/v1/account`, and keeps that login in memory for up to 10 minutes. The key is read-only:
it cannot buy, change or delete anything.

## Connection requirements

The plugin connects to two hosts:

- `proxmint.com` over HTTPS, to read the proxy login
- the proxy gateway `gw.proxmint.com` on port 823, for every page

The page is fetched by the exit IP, so the Dify host never connects to the target site itself. A self-hosted Dify
behind a firewall must allow outbound TCP to `gw.proxmint.com:823`.

## Good to know

- Bandwidth comes out of your own Proxmint product. City targeting meters at twice the bandwidth on residential,
  datacenter and mobile ([targeting](https://proxmint.com/docs/targeting)).
- The proxies reach web ports 80, 443, 8080, 8443, 8888 and 8090 ([port access](https://proxmint.com/docs/ports)).
- A short list of sites, mostly banking and government, is refused by the network
  ([blocked websites](https://proxmint.com/docs/blocked-websites)).
- When the gateway refuses a request (no bandwidth left, no IP matching the targeting, a blocked site), the tool fails
  with a one-line message saying what to change ([error codes](https://proxmint.com/docs/errors)).
- The tool does not run JavaScript. It reads what the server sends.

Full guide: [proxmint.com/docs/dify](https://proxmint.com/docs/dify)

## Source and support

- Source: [github.com/proxmint/dify-proxmint](https://github.com/proxmint/dify-proxmint)
- Support: support@proxmint.com
- Privacy: [PRIVACY.md](https://github.com/proxmint/dify-proxmint/blob/main/PRIVACY.md)
