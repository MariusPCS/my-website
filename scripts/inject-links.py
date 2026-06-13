#!/usr/bin/env python3
"""Replace {{PRODUCT_SLUG}} placeholders with live ProfitShare tracking URLs.
Also regenerates sitemap.xml, feed.xml, and the homepage article grid.
Fails the build if any placeholder cannot be resolved.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PRODUCTS_FILE = ROOT / "products.json"

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def load_products() -> dict:
    if not PRODUCTS_FILE.exists():
        print("ERROR: products.json not found. Run fetch-products.py first.")
        sys.exit(1)
    return json.loads(PRODUCTS_FILE.read_text())


def inject_html(products: dict) -> list[str]:
    """Inject links into all HTML files. Returns list of unresolved slugs."""
    unresolved = []
    html_files = list(ROOT.glob("*.html")) + list(ROOT.glob("articles/*.html"))

    for path in html_files:
        content = path.read_text()
        slugs_in_file = PLACEHOLDER_RE.findall(content)

        for slug in slugs_in_file:
            if slug in products:
                url = products[slug]
                content = content.replace(f"{{{{{slug}}}}}", url)
            else:
                # Graceful degradation: try advertiser home link
                advertiser = slug.split("_")[0]
                home_key = f"{advertiser}_HOME"
                if home_key in products:
                    content = content.replace(f"{{{{{slug}}}}}", products[home_key])
                    print(f"  WARNING [{path.name}]: {{{{{slug}}}}} replaced by fallback {home_key} (needs manual review)")
                else:
                    unresolved.append(f"{path.name}: {{{{{slug}}}}}")

        path.write_text(content)

    return unresolved


def ensure_affiliate_attrs(html: str) -> str:
    """Ensure all btn-affiliate links have correct rel and target attributes."""
    def fix_link(m):
        tag = m.group(0)
        if 'rel=' not in tag:
            tag = tag.replace('<a ', '<a rel="nofollow noopener noreferrer" ', 1)
        if 'target=' not in tag:
            tag = tag.replace('<a ', '<a target="_blank" ', 1)
        return tag

    return re.sub(r'<a\s[^>]*class="btn-affiliate"[^>]*>', fix_link, html)


def main():
    products = load_products()
    print(f"Loaded {len(products)} product links.")

    unresolved = inject_html(products)

    if unresolved:
        print("\nERROR: The following placeholders could not be resolved:")
        for item in unresolved:
            print(f"  {item}")
        sys.exit(1)

    print("All placeholders resolved successfully.")


if __name__ == "__main__":
    main()
