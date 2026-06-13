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


def fetch(api_user: str, api_key: str) -> dict:
    """Return a dict mapping product slug → tracking URL."""
    aff_code = os.environ.get("PROFITSHARE_AFF_CODE", "")

    # 2Performant auth: user_email + user_token as query params
    auth_params = f"user_email={urllib.parse.quote(api_user)}&user_token={api_key}"

    headers = {"Accept": "application/json"}

    # Fetch accepted affiliate programs
    url = f"{API_BASE}/affiliate/programs?filter[status]=accepted&per_page=100&{auth_params}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        programs_data = json.loads(resp.read())

    products = {}

    for program in programs_data.get("programs", []):
        unique = program.get("unique_code", "")
        slug = program.get("slug", "").upper().replace("-", "_")

        if unique and slug:
            tracking_url = (
                f"https://event.2performant.com/events/click"
                f"?ad_type=banner&unique={unique}&aff_code={aff_code}"
            )
            products[f"{slug}_HOME"] = tracking_url

    # Fetch product deep links if available
    try:
        url2 = f"{API_BASE}/affiliate/product_feeds?per_page=200&{auth_params}"
        req2 = urllib.request.Request(url2, headers=headers)
        with urllib.request.urlopen(req2, timeout=15) as resp:
            feeds_data = json.loads(resp.read())
        for item in feeds_data.get("product_feeds", []):
            slug = item.get("slug", "").upper().replace("-", "_")
            item_url = item.get("url", "")
            if slug and item_url:
                products[slug] = item_url
    except Exception:
        pass  # Deep links optional

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
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"WARNING: ProfitShare API returned HTTP {e.code}: {e.reason}")
        print(f"Response body: {body}")
        if FALLBACK.exists():
            print("Using cached product data.")
            shutil.copy(FALLBACK, OUTPUT)
        else:
            write_stub(f"API error {e.code} and no cache available")
    except urllib.error.URLError as e:
        print(f"WARNING: ProfitShare API unreachable: {e}")
        if FALLBACK.exists():
            print("Using cached product data.")
            shutil.copy(FALLBACK, OUTPUT)
        else:
            write_stub("API unreachable and no cache available")


if __name__ == "__main__":
    main()
