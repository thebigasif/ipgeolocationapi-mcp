"""ipgeolocationapi.io MCP server.

Lets Claude Desktop, Cursor, and any MCP-compatible AI call our IP intelligence
endpoints as native tools. No custom code for the user: npx/uvx-style run or a
plain python script. The free tier is keyless (5,000 lookups/day), paid modules
(security, company, bulk) need an API key from the dashboard.

Run (stdio, for Claude Desktop / Cursor):
    python mcp_server.py
Config (claude_desktop_config.json):
    {"mcpServers": {"ipgeolocationapi": {
        "command": "python",
        "args": ["/abs/path/to/mcp_server.py"],
        "env": {"IPGEO_API_KEY": "ipa_your_key_optional"}
    }}}
"""
from __future__ import annotations

import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

BASE = os.environ.get("IPGEO_BASE", "https://ipgeolocationapi.io")
KEY = os.environ.get("IPGEO_API_KEY", "")

mcp = FastMCP("ipgeolocationapi")


def _get(path: str, params: dict | None = None) -> dict:
    headers = {"accept": "application/json"}
    if KEY:
        headers["X-API-Key"] = KEY
    r = httpx.get(f"{BASE}{path}", params=params or {}, headers=headers, timeout=20)
    try:
        return r.json()
    except Exception:
        return {"success": False, "status": r.status_code, "body": r.text[:400]}


@mcp.tool()
async def ip_lookup(ip: str, fields: str = "") -> dict:
    """Look up an IPv4, IPv6 address or domain. Returns country, region, city,
    coordinates, timezone, currency, ASN and connection info in one call.

    Args:
        ip: The address or domain to look up, e.g. "8.8.8.8" or "cloudflare.com".
        fields: Optional comma list to slim the response, e.g. "ip,country,city,connection.asn".
    """
    if not ip or not ip.strip():
        return {"success": False, "message": "Provide an IP or domain, e.g. 8.8.8.8"}
    params = {"fields": fields} if fields else None
    return _get(f"/{ip.strip()}", params)


@mcp.tool()
async def security_check(ip: str) -> dict:
    """Get VPN, proxy, Tor, hosting and relay verdicts with confidence scores
    for an IP. Paid module: needs a Business or Max API key (set IPGEO_API_KEY).

    Args:
        ip: The address to check, e.g. "45.83.91.5".
    """
    return _get(f"/{ip}", {"security": "1", "fields": "ip,security"})


@mcp.tool()
async def company_lookup(ip: str) -> dict:
    """Get the operating company behind an IP: PTR hostname, organization name,
    type and registration country. Paid module: Business or Max key required.

    Args:
        ip: The address to look up, e.g. "8.8.8.8".
    """
    return _get(f"/{ip}", {"company": "1", "fields": "ip,company"})


@mcp.tool()
async def asn_lookup(asn: str) -> dict:
    """Look up an autonomous system by number or org name: prefixes announced,
    route counts, network type. Free.

    Args:
        asn: AS number, e.g. "13335".
    """
    return _get("/asn", {"asn": asn})


@mcp.tool()
async def timezone_info(ip: str) -> dict:
    """Get current local time, UTC offset and DST transition dates for the
    timezone an IP lives in. Free.

    Args:
        ip: The address to locate, e.g. "8.8.8.8" or "1.1.1.1".
    """
    return _get(f"/{ip}", {"fields": "ip,country,city,timezone"})


@mcp.tool()
async def timezone_convert(time: str, from_zone: str, to_zone: str) -> dict:
    """Convert a timestamp between two IANA timezones. Free.

    Args:
        time: ISO timestamp, e.g. "2026-09-08T14:30:00".
        from_zone: Source IANA zone, e.g. "America/New_York".
        to_zone: Target IANA zone, e.g. "Asia/Tokyo".
    """
    return _get("/timezone/convert", {"time": time, "from": from_zone, "to": to_zone})


@mcp.tool()
async def astronomy(ip: str = "", latitude: float = None, longitude: float = None, date: str = "") -> dict:
    """Sunrise, sunset, twilight tiers, golden and blue hour, moon phase and sun
    position. Free. Give an IP, or exact coordinates with an optional date
    (YYYY-MM-DD).

    Args:
        ip: The address whose location to compute for, e.g. "8.8.8.8".
        latitude: Decimal latitude if you know the spot, e.g. 40.71.
        longitude: Decimal longitude if you know the spot, e.g. -74.01.
        date: Optional date (YYYY-MM-DD); defaults to today.
    """
    params = {}
    if latitude is not None and longitude is not None:
        params = {"lat": latitude, "lon": longitude}
    elif ip:
        params = {"ip": ip}
    else:
        return {"success": False, "message": "Give an IP, or latitude and longitude."}
    if date:
        params["date"] = date
    return _get("/astronomy", params)


@mcp.tool()
async def parse_user_agent(ua: str = "") -> dict:
    """Parse a User-Agent string into browser, engine, OS, device class and bot
    verdict. Free. Empty ua parses the caller's own agent.

    Args:
        ua: The User-Agent string to parse.
    """
    return _get("/useragent", {"ua": ua} if ua else None)


@mcp.tool()
async def abuse_contact(ip: str) -> dict:
    """Find the abuse contact (mailbox, phone, organization, range) for an IP
    from registry data. Free.

    Args:
        ip: The attacking or investigated address, e.g. "185.220.101.1".
    """
    return _get("/abuse", {"ip": ip})


@mcp.tool()
async def bulk_lookup(ips: str) -> dict:
    """Look up up to 100 IPv4/IPv6 addresses in one call, order preserved.
    Paid module: Business or Max key required (set IPGEO_API_KEY).

    Args:
        ips: Comma-separated addresses, e.g. "8.8.8.8,1.1.1.1".
    """
    return _get("/bulk", {"ips": ips, "fields": "ip,country,city,connection.asn"})


if __name__ == "__main__":
    mcp.run()
