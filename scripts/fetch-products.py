#!/usr/bin/env python3
"""Fetch active product/program data from ProfitShare (2Performant) API.

Outputs products.json (gitignored). Falls back to cached artifact if API is down.
Auth: 2Performant uses user_email + user_token as query params.
"""

import json
import os
import shutil
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    import requests
    USE_REQUESTS = True
except ImportError:
    USE_REQUESTS = False

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "products.json"
FALLBACK = ROOT / "products_cache.json"

API_BASE = "https://api.2performant.com"

STUB = {
    "EMAG_HOME": "#affiliate-link-pending",
    "ALTEX_HOME": "#affiliate-link-pending",
}


def write_stub(reason: str) -> None:
    print(f"WARNING: {reason}. Using stub links — add secrets to enable real links.")
    OUTPUT.write_text(json.dumps(STUB, indent=2))


BROWSER_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://app.2performant.com/",
    "Origin": "https://app.2performant.com",
    "Connection": "keep-alive",
}


def fetch(api_user: str, api_key: str) -> dict:
    """Return a dict mapping product slug → tracking URL."""
    aff_code = os.environ.get("PROFITSHARE_AFF_CODE", "")
    params = {"user_email": api_user, "user_token": api_key, "filter[status]": "accepted", "per_page": 100}

    if USE_REQUESTS:
        session = requests.Session()
        session.headers.update(BROWSER_HEADERS)
        resp = session.get(f"{API_BASE}/affiliate/programs", params=params, timeout=20)
        resp.raise_for_status()
        programs_data = resp.json()
    else:
        import urllib.parse  # noqa: PLC0415
        qs = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{API_BASE}/affiliate/programs?{qs}", headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            programs_data = json.loads(r.read())

    products = {}
    for program in programs_data.get("programs", []):
        unique = program.get("unique_code", "")
        slug = program.get("slug", "").upper().replace("-", "_")
        if unique and slug:
            products[f"{slug}_HOME"] = (
                f"https://event.2performant.com/events/click"
                f"?ad_type=banner&unique={unique}&aff_code={aff_code}"
            )

    # Deep links (optional)
    try:
        if USE_REQUESTS:
            r2 = session.get(f"{API_BASE}/affiliate/product_feeds",
                             params={"user_email": api_user, "user_token": api_key, "per_page": 200},
                             timeout=20)
            feeds_data = r2.json() if r2.ok else {}
        else:
            import urllib.parse  # noqa: PLC0415
            qs2 = urllib.parse.urlencode({"user_email": api_user, "user_token": api_key, "per_page": 200})
            req2 = urllib.request.Request(f"{API_BASE}/affiliate/product_feeds?{qs2}", headers=BROWSER_HEADERS)
            with urllib.request.urlopen(req2, timeout=20) as r:
                feeds_data = json.loads(r.read())
        for item in feeds_data.get("product_feeds", []):
            slug = item.get("slug", "").upper().replace("-", "_")
            item_url = item.get("url", "")
            if slug and item_url:
                products[slug] = item_url
    except Exception:
        pass

    return products


def main():
    import urllib.parse  # noqa: PLC0415

    api_key = os.environ.get("PROFITSHARE_API_KEY", "")
    # Try the registered email first; fall back to the API user identifier
    api_user = os.environ.get("PROFITSHARE_USER_EMAIL", "") or os.environ.get("PROFITSHARE_API_USER", "")

    if not api_key or not api_user:
        write_stub("API credentials not configured")
        sys.exit(0)

    try:
        products = fetch(api_user, api_key)
        if not products:
            write_stub("API returned no programs (account may not be approved yet)")
            sys.exit(0)
        OUTPUT.write_text(json.dumps(products, indent=2))
        FALLBACK.write_text(json.dumps(products, indent=2))
        print(f"Fetched {len(products)} affiliate links → {OUTPUT}")
    except Exception as e:
        # Covers requests.HTTPError, urllib.error.HTTPError, urllib.error.URLError, etc.
        err_body = ""
        if hasattr(e, "response") and e.response is not None:
            err_body = e.response.text[:300]
        elif hasattr(e, "read"):
            err_body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"WARNING: ProfitShare API error: {e}")
        if err_body:
            print(f"Response: {err_body}")
        if FALLBACK.exists():
            print("Using cached product data.")
            shutil.copy(FALLBACK, OUTPUT)
        else:
            write_stub("API error and no cache available")


if __name__ == "__main__":
    main()
