# ipgeolocationapi

Zero-dependency Python client for [ipgeolocationapi.io](https://ipgeolocationapi.io),
the free IP geolocation API. Stdlib only, Python 3.9+.

## Install

```bash
pip install ipgeolocateio
```

## Quickstart (free tier, no key)

```python
from ipgeolocateio import Client

c = Client()
geo = c.lookup("8.8.8.8")
print(geo["country"], geo["connection"]["asn"], geo["timezone"]["id"])
```

The free tier works with no API key: 5,000 requests/day, no signup.

## Paid features

```python
c = Client("ipa_YOUR_KEY")   # from https://ipgeolocationapi.io/dashboard

c.security("1.1.1.1")        # VPN / proxy / Tor verdicts + threat score
c.asn(13335)                 # autonomous system lookup
c.timezone_convert("America/New_York", "Asia/Tokyo")
c.astronomy(lat=52.52, lon=13.405)   # sunrise, golden hour, moon
c.bulk(["8.8.8.8", "1.1.1.1"])
```

## Error handling

```python
from ipgeolocationapi import RateLimitError, PlanError

try:
    geo = c.lookup("10.0.0.1")
except PlanError:
    ...   # endpoint needs a paid plan
except RateLimitError as e:
    ...   # e.retry_after seconds until the window resets
```

## API surface

| Method | Endpoint |
|---|---|
| `lookup(ip, fields, excludes, lang, security)` | `GET /{ip or domain}` |
| `asn(number)` | `GET /asn?asn=` |
| `timezone_convert(from, to, time)` | `GET /timezone/convert` |
| `astronomy(ip, lat, lon, date)` | `GET /astronomy` |
| `useragent(ua)` | `GET /useragent` |
| `abuse(ip)` | `GET /abuse` |
| `bulk(ips, fields)` | `POST /bulk` |

Full docs: <https://ipgeolocationapi.io/docs> · OpenAPI 3.1: <https://ipgeolocationapi.io/openapi.json>

MIT License.
