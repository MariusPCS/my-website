#!/usr/bin/env python3
"""Verify all internal links between HTML pages resolve to existing files.
Fails the build on broken internal links.
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent

HREF_RE = re.compile(r'href="([^"#?]+)"')


def is_internal(href: str) -> bool:
    parsed = urlparse(href)
    return not parsed.scheme and not parsed.netloc and href.endswith(".html")


def resolve(source: Path, href: str) -> Path:
    if href.startswith("/"):
        return ROOT / href.lstrip("/")
    return (source.parent / href).resolve()


def main():
    html_files = [p for p in ROOT.rglob("*.html") if "node_modules" not in p.parts]
    broken = []

    for source in html_files:
        content = source.read_text()
        for href in HREF_RE.findall(content):
            if not is_internal(href):
                continue
            target = resolve(source, href)
            if not target.exists():
                broken.append(f"{source.relative_to(ROOT)} → {href} (not found)")

    if broken:
        print("ERROR: Broken internal links detected:")
        for b in broken:
            print(f"  {b}")
        sys.exit(1)

    print(f"Internal link check passed: {len(html_files)} files scanned, no broken links.")


if __name__ == "__main__":
    main()
