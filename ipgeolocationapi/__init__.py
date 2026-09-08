"""ipgeolocationapi.io Python SDK.

Zero-dependency (stdlib only). Python 3.9+.

    from ipgeolocationapi import Client
    c = Client()                # free tier, no key
    c.lookup("8.8.8.8")
    c = Client("ipa_YOUR_KEY")  # paid features
    c.security("1.1.1.1")
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://ipgeolocationapi.io"
__version__ = "1.0.0"


class APIError(Exception):
    def __init__(self, message: str, status: int = 0, body: dict | None = None):
        super().__init__(message)
        self.status = status
        self.body = body or {}


class Client:
    def __init__(self, api_key: str | None = None, base_url: str = BASE, timeout: int = 15):
        self.api_key = api_key
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    # -- core ------------------------------------------------------------
    def _get(self, path: str, params: dict | None = None) -> dict:
        q = dict(params or {})
        if self.api_key and "key" not in q:
            q["key"] = self.api_key
        url = self.base + path
        if q:
            url += "?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"User-Agent": f"ipgeolocationapi-py/{__version__}"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode())
            except Exception:
                body = {}
            raise APIError(body.get("message") or str(e), e.code, body) from None

    # -- endpoints ---------------------------------------------------------
    def me(self, **params) -> dict:
        """Look up the caller's own IP."""
        return self._get("/", params)

    def lookup(self, ip: str, fields: str | None = None, excludes: str | None = None,
               security: bool = False, company: bool = False, **params) -> dict:
        """Geolocation lookup for an IPv4/IPv6 address."""
        p = {"fields": fields, "excludes": excludes, "security": int(security),
             "company": int(company), **params}
        return self._get(f"/{ip}", {k: v for k, v in p.items() if v})

    def security(self, ip: str) -> dict:
        """Security/VPN/proxy signals (paid)."""
        return self._get(f"/{ip}", {"security": 1})

    def company(self, ip: str) -> dict:
        """Company + hostname block (paid)."""
        return self._get(f"/{ip}", {"company": 1})

    def timezone_convert(self, from_tz: str, to_tz: str, time: str | None = None) -> dict:
        """Convert a wall-clock time between IANA timezones."""
        p = {"from": from_tz, "to": to_tz, "time": time}
        return self._get("/timezone/convert", {k: v for k, v in p.items() if v})

    def astronomy(self, ip: str | None = None, lat: float | None = None,
                  lon: float | None = None, date: str | None = None) -> dict:
        """Sun/moon events: sunrise, golden hour, moonrise, positions."""
        p = {"ip": ip, "lat": lat, "lon": lon, "date": date}
        return self._get("/astronomy", {k: v for k, v in p.items() if v is not None})

    def useragent(self, ua: str | None = None) -> dict:
        """Parse a user-agent string (defaults to a browser-ish UA)."""
        return self._get("/useragent", {"ua": ua} if ua else None)

    def asn(self, asn: int | str) -> dict:
        """ASN lookup: org, type, route counts, prefixes."""
        return self._get("/asn", {"asn": asn})

    def abuse(self, ip: str) -> dict:
        """Abuse contact for an IP (RDAP)."""
        return self._get("/abuse", {"ip": ip})

    def bulk(self, ips: list[str], fields: str | None = None) -> list:
        """Bulk lookup up to 100 IPs (paid). Returns a list in request order."""
        return list(self._get("/bulk", {"ips": ",".join(ips), "fields": fields}))

    def bulk_async(self, ips: list[str], fields: str | None = None,
                   webhook_url: str | None = None) -> dict:
        """Submit up to 1,000,000 IPs as a background job (paid)."""
        payload = {"ips": ips}
        if fields:
            payload["fields"] = fields
        if webhook_url:
            payload["webhook_url"] = webhook_url
        req = urllib.request.Request(
            self.base + "/bulk/async",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "X-API-Key": self.api_key or ""},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise APIError(str(e), e.code) from None

    def bulk_status(self, job_id: str) -> dict:
        return self._get(f"/bulk/async/{job_id}")

    def bulk_download(self, job_id: str) -> bytes:
        """Gzipped JSON bytes of a finished job."""
        url = f"{self.base}/bulk/async/{job_id}/download"
        req = urllib.request.Request(url, headers={"X-API-Key": self.api_key or ""})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
