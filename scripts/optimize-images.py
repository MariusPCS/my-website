#!/usr/bin/env python3
"""Convert PNG/JPG images in assets/images/ to WebP and resize if > 1200px wide.
Skips unchanged files. Requires Pillow: pip install Pillow
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Skipping image optimization.")
    sys.exit(0)

ROOT = Path(__file__).parent.parent
IMAGES_DIR = ROOT / "assets" / "images"
MAX_WIDTH = 1200


def optimize(src: Path) -> None:
    webp_path = src.with_suffix(".webp")

    # Skip if WebP already exists and is newer than source
    if webp_path.exists() and webp_path.stat().st_mtime >= src.stat().st_mtime:
        return

    with Image.open(src) as img:
        img = img.convert("RGB")
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
        img.save(webp_path, "WEBP", quality=82, method=6)
        print(f"  Optimized: {src.name} → {webp_path.name} ({webp_path.stat().st_size // 1024}KB)")


def main():
    if not IMAGES_DIR.exists():
        print("No images directory found. Skipping.")
        sys.exit(0)

    sources = list(IMAGES_DIR.glob("*.png")) + list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.jpeg"))

    if not sources:
        print("No PNG/JPG images found. Skipping.")
        sys.exit(0)

    for src in sources:
        optimize(src)

    print(f"Image optimization complete: {len(sources)} images processed.")


if __name__ == "__main__":
    main()
