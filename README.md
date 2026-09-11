# ipgeolocationapi-mcp

[![M8ven Score](https://m8ven.ai/badge/mcp/thebigasif/ipgeolocationapi-mcp)](https://m8ven.ai/mcp/thebigasif/ipgeolocationapi-mcp)

MCP server for [ipgeolocationapi.io](https://ipgeolocationapi.io): IP intelligence
as native tools for Claude Desktop, Cursor, and any MCP-compatible AI.

Ask "where is this visitor from, and is the IP a VPN?" and the AI fetches live
data directly. No custom code.

## Install (30 seconds)

Add to `claude_desktop_config.json` (Claude Desktop > Settings > Developer):

```json
{
  "mcpServers": {
    "ipgeolocationapi": {
      "command": "npx",
      "args": ["-y", "ipgeolocationapi-mcp"],
      "env": {
        "IPGEO_API_KEY": "ipa_optional_paid_key"
      }
    }
  }
}
```

Restart Claude Desktop. Done. The first run creates a small Python runtime
(one time); Linux ships with a compatible Python by default; on macOS install Python 3.10+ from python.org or Homebrew if the wrapper cannot find one.

Cursor and other MCP hosts: same shape, point the command at this package.

## The 10 tools

| Tool | What it returns | Tier |
|---|---|---|
| `ip_lookup` | country, region, city, coordinates, timezone, currency, ASN | free, keyless |
| `security_check` | VPN, proxy, Tor, hosting, relay verdicts + threat score | paid |
| `company_lookup` | organization, registration country, PTR hostname | paid |
| `asn_lookup` | prefixes, route counts, network type | free |
| `timezone_info` | local time, offset, DST transitions | free |
| `timezone_convert` | convert timestamps between IANA zones | free |
| `astronomy` | sunrise, sunset, twilight tiers, golden hour, moon phase | free |
| `parse_user_agent` | browser, engine, OS, device class, bot verdict | free |
| `abuse_contact` | registry abuse mailbox and phone per range | free |
| `bulk_lookup` | up to 100 addresses per call, order preserved | paid |

Free tier: 5,000 calls/day, no key, no signup. Paid modules (security, company,
bulk) need a Business or Max key from the [dashboard](https://ipgeolocationapi.io/dashboard).

## Environment variables

- `IPGEO_API_KEY` - optional. Unlocks the paid tools.
- `IPGEO_BASE` - optional. Defaults to `https://ipgeolocationapi.io`.
- `IPGEO_PYTHON` - optional. Explicit Python 3.10+ interpreter path.

## Plain Python (no npm)

```bash
curl -O https://ipgeolocationapi.io/mcp/mcp_server.py
pip install "mcp==1.26.0" httpx
python mcp_server.py
```

## License

MIT. The API terms apply to the data: https://ipgeolocationapi.io/terms
