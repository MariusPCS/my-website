#!/usr/bin/env python3
"""Regenerate sitemap.xml, feed.xml, and the homepage article grid from articles.json."""

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
BASE_URL = "https://mariuspcs.github.io/my-website"

STATIC_PAGES = [
    ("", "weekly", "1.0"),
    ("about.html", "monthly", "0.5"),
]


def load_articles() -> list:
    p = ROOT / "articles.json"
    return json.loads(p.read_text()) if p.exists() else []


# ── Sitemap ──────────────────────────────────────────────────────────────────

def generate_sitemap(articles: list) -> None:
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for path, freq, priority in STATIC_PAGES:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{BASE_URL}/{path}"
        ET.SubElement(url, "changefreq").text = freq
        ET.SubElement(url, "priority").text = priority

    for article in articles:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{BASE_URL}/articles/{article['slug']}.html"
        ET.SubElement(url, "lastmod").text = article.get("updated", article["published"])
        ET.SubElement(url, "changefreq").text = "monthly"
        ET.SubElement(url, "priority").text = "0.8"

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    out = ROOT / "sitemap.xml"
    tree.write(out, xml_declaration=True, encoding="utf-8")
    print(f"Generated: {out} ({len(articles)} articles + {len(STATIC_PAGES)} static pages)")


# ── RSS Feed ─────────────────────────────────────────────────────────────────

def generate_feed(articles: list) -> None:
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "TechPicks"
    ET.SubElement(channel, "link").text = BASE_URL
    ET.SubElement(channel, "description").text = "Tech reviews and buying guides"
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )

    for article in articles[:20]:  # RSS: latest 20
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article["title"]
        ET.SubElement(item, "link").text = f"{BASE_URL}/articles/{article['slug']}.html"
        ET.SubElement(item, "description").text = article.get("description", "")
        ET.SubElement(item, "pubDate").text = datetime.fromisoformat(
            article["published"]
        ).strftime("%a, %d %b %Y 00:00:00 +0000")
        ET.SubElement(item, "guid").text = f"{BASE_URL}/articles/{article['slug']}.html"
        ET.SubElement(item, "category").text = article.get("category", "")

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    out = ROOT / "feed.xml"
    tree.write(out, xml_declaration=True, encoding="utf-8")
    print(f"Generated: {out} ({min(len(articles), 20)} items)")


# ── Homepage article grid ─────────────────────────────────────────────────────

def generate_article_card(article: dict) -> str:
    slug = article["slug"]
    title = article["title"]
    description = article.get("description", "")
    category = article.get("category", "")
    published = article.get("published", "")
    rating = article.get("rating", 0)
    stars = "&#9733;" * int(rating) + "&#9734;" * (5 - int(rating))

    return f"""        <article class="article-card">
          <a href="articles/{slug}.html">
            <picture>
              <source srcset="assets/images/{slug}.webp" type="image/webp" />
              <img src="assets/images/{slug}.jpg" alt="{title}" loading="lazy" width="400" height="225" />
            </picture>
          </a>
          <div class="card-body">
            <span class="category-tag">{category.title()}</span>
            <h2><a href="articles/{slug}.html">{title}</a></h2>
            <p>{description}</p>
            <div class="card-footer">
              <span class="star-rating" aria-label="Rating: {rating} out of 5">{stars}</span>
              <time datetime="{published}">{published}</time>
            </div>
          </div>
        </article>"""


def update_homepage(articles: list) -> None:
    index_path = ROOT / "index.html"
    if not index_path.exists():
        print("WARNING: index.html not found, skipping grid update.")
        return

    content = index_path.read_text()
    cards = "\n".join(generate_article_card(a) for a in articles)
    grid_block = f"      <!-- ARTICLE_GRID_START -->\n{cards}\n      <!-- ARTICLE_GRID_END -->"

    import re
    updated = re.sub(
        r"<!-- ARTICLE_GRID_START -->.*?<!-- ARTICLE_GRID_END -->",
        grid_block,
        content,
        flags=re.DOTALL,
    )
    index_path.write_text(updated)
    print(f"Updated homepage grid: {len(articles)} articles")


def main():
    articles = load_articles()
    generate_sitemap(articles)
    generate_feed(articles)
    update_homepage(articles)


if __name__ == "__main__":
    main()
