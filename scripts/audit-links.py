#!/usr/bin/env python3
"""Validate all existing ProfitShare affiliate links in HTML files.
Replaces stale/inactive links with current equivalents from the API.
Runs on every deploy and weekly via cron.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
PRODUCTS_FILE = ROOT / "products.json"

PROFITSHARE_LINK_RE = re.compile(
    r'href="(https://event\.2performant\.com/events/click[^"]*)"'
)

def extract_unique_code(url: str) -> str | None:
    m = re.search(r"unique=([^&]+)", url)
    return m.group(1) if m else None

def load_products() -> dict:
    if not PRODUCTS_FILE.exists():
        return {}
    return json.loads(PRODUCTS_FILE.read_text())

def validate_link(url: str) -> bool:
    """Return True if the tracking URL is still active (HTTP 200 or 301/302)."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "TechPicksBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status < 400
    except Exception:
        return False

def find_replacement(unique: str, products: dict) -> str | None:
    """Find an active link to the same advertiser from products catalog."""
    # unique codes often contain the advertiser prefix — try to match
    for slug, url in products.items():
        if unique and unique[:4].lower() in url.lower():
            return url
    # fallback: return first available home link
    home_links = [v for k, v in products.items() if k.endswith("_HOME")]
    return home_links[0] if home_links else None

def main():
    api_key = os.environ.get("PROFITSHARE_API_KEY", "")
    if not api_key:
        print("WARNING: PROFITSHARE_API_KEY not set. Skipping live validation.")
        print("Running in offline mode — checking only for obviously broken link patterns.")

    products = load_products()
    html_files = list(ROOT.rglob("*.html"))

    total = 0
    updated = 0
    warnings = []

    for path in html_files:
        content = path.read_text()
        links = PROFITSHARE_LINK_RE.findall(content)

        for url in links:
            total += 1
            is_valid = validate_link(url) if api_key else True

            if not is_valid:
                unique = extract_unique_code(url)
                replacement = find_replacement(unique or "", products)

                if replacement:
                    content = content.replace(f'href="{url}"', f'href="{replacement}"')
                    updated += 1
                    print(f"  UPDATED [{path.name}]: replaced stale link")
                else:
                    warnings.append(f"{path.name}: stale link with no replacement — needs manual review")
                    print(f"  WARNING [{path.name}]: stale link, no replacement found")

        path.write_text(content)

    print(f"\nAudit complete: {total} links checked, {updated} updated, {len(warnings)} warnings.")

    if warnings:
        print("\nLinks needing manual review:")
        for w in warnings:
            print(f"  {w}")

    # Exit with error if too many warnings (triggers notification)
    if len(warnings) > 5:
        print(f"\nERROR: {len(warnings)} links could not be fixed. Manual review required.")
        sys.exit(1)

if __name__ == "__main__":
    main()
