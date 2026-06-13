#!/usr/bin/env python3
"""Fetch active product/program data from ProfitShare (2Performant) API.

Outputs products.json (gitignored). Falls back to cached artifact if API is down.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "products.json"
FALLBACK = ROOT / "products_cache.json"

API_BASE = "https://api.2performant.com"


def fetch(api_key: str) -> dict:
    """Return a dict mapping product slug → tracking URL."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    # Fetch active affiliate programs the user is approved for
    req = urllib.request.Request(
        f"{API_BASE}/affiliate/programs?filter[status]=accepted&per_page=100",
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        programs_data = json.loads(resp.read())

    products = {}

    # Build home-page fallback links for each accepted program
    for program in programs_data.get("programs", []):
        unique = program.get("unique_code", "")
        slug = program.get("slug", "").upper().replace("-", "_")
        aff_code = os.environ.get("PROFITSHARE_AFF_CODE", "")

        if unique and slug:
            tracking_url = (
                f"https://event.2performant.com/events/click"
                f"?ad_type=banner&unique={unique}&aff_code={aff_code}"
            )
            products[f"{slug}_HOME"] = tracking_url

    # Fetch product feeds (deep links) if available
    req2 = urllib.request.Request(
        f"{API_BASE}/affiliate/product_feeds?per_page=200",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req2, timeout=15) as resp:
            feeds_data = json.loads(resp.read())
        for item in feeds_data.get("product_feeds", []):
            slug = item.get("slug", "").upper().replace("-", "_")
            url = item.get("url", "")
            if slug and url:
                products[slug] = url
    except Exception:
        pass  # Product feeds are optional; home links are sufficient fallback

    return products


def main():
    api_key = os.environ.get("PROFITSHARE_API_KEY", "")

    if not api_key:
        print("WARNING: PROFITSHARE_API_KEY not set.")
        if FALLBACK.exists():
            print(f"Using fallback: {FALLBACK}")
            import shutil
            shutil.copy(FALLBACK, OUTPUT)
            sys.exit(0)
        else:
            print("WARNING: No API key and no fallback cache. Creating stub products.json.")
            print("Add PROFITSHARE_API_KEY to GitHub Secrets to enable real affiliate links.")
            stub = {"EMAG_HOME": "#affiliate-link-pending", "ALTEX_HOME": "#affiliate-link-pending"}
            OUTPUT.write_text(json.dumps(stub, indent=2))
            sys.exit(0)

    try:
        products = fetch(api_key)
        OUTPUT.write_text(json.dumps(products, indent=2))
        # Update the fallback cache for next time
        FALLBACK.write_text(json.dumps(products, indent=2))
        print(f"Fetched {len(products)} product links → {OUTPUT}")
    except urllib.error.URLError as e:
        print(f"WARNING: ProfitShare API unreachable: {e}")
        if FALLBACK.exists():
            print(f"Falling back to cached data: {FALLBACK}")
            import shutil
            shutil.copy(FALLBACK, OUTPUT)
        else:
            print("ERROR: API down and no fallback cache available.")
            sys.exit(1)


if __name__ == "__main__":
    main()
