#!/usr/bin/env python3
"""Scaffold a new article: creates articles/<slug>.html and updates articles.json."""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent

def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/new-article.py \"Article Title\" category")
        print("Categories: laptops, phones, tablets, peripherals, smart-home, audio")
        sys.exit(1)

    title = sys.argv[1]
    category = sys.argv[2].lower()
    slug = slugify(title)
    today = date.today().isoformat()
    article_path = ROOT / "articles" / f"{slug}.html"

    if article_path.exists():
        print(f"Error: {article_path} already exists.")
        sys.exit(1)

    # Write article HTML scaffold
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | TechPicks</title>
  <meta name="description" content="WRITE DESCRIPTION HERE (max 160 chars)" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://mariuspcs.github.io/my-website/articles/{slug}.html" />

  <!-- Open Graph -->
  <meta property="og:title" content="{title} | TechPicks" />
  <meta property="og:description" content="WRITE DESCRIPTION HERE" />
  <meta property="og:image" content="https://mariuspcs.github.io/my-website/assets/images/{slug}.webp" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:url" content="https://mariuspcs.github.io/my-website/articles/{slug}.html" />

  <!-- JSON-LD: Review / Article -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Review",
    "headline": "{title}",
    "datePublished": "{today}",
    "dateModified": "{today}",
    "author": {{
      "@type": "Person",
      "name": "TechPicks Editorial"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "TechPicks",
      "url": "https://mariuspcs.github.io/my-website/"
    }},
    "reviewRating": {{
      "@type": "Rating",
      "ratingValue": "4.5",
      "bestRating": "5"
    }}
  }}
  </script>

  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#0f1115" media="(prefers-color-scheme: dark)" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
  <a href="#main" class="skip-link">Skip to main content</a>

  <header>
    <a href="../index.html" class="logo">Tech<span>Picks</span></a>
    <div class="header-right">
      <nav aria-label="Main navigation">
        <a href="../index.html">Home</a>
        <a href="../index.html#categories">Categories</a>
        <a href="../about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main">
    <article class="article-full">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a> &rsaquo;
        <a href="../index.html#categories">{category.title()}</a> &rsaquo;
        <span>{title}</span>
      </nav>

      <header class="article-header">
        <span class="category-tag">{category.title()}</span>
        <h1>{title}</h1>
        <p class="article-meta">
          <time datetime="{today}">{date.today().strftime("%B %d, %Y")}</time>
          &middot; By TechPicks Editorial
        </p>
        <div class="star-rating" aria-label="Rating: 4.5 out of 5">
          <span>&#9733;&#9733;&#9733;&#9733;&#9734;</span> 4.5 / 5
        </div>
      </header>

      <!-- WRITE INTRO HERE -->
      <p>INTRO PARAGRAPH HERE.</p>

      <picture>
        <source srcset="../assets/images/{slug}.webp" type="image/webp" />
        <img src="../assets/images/{slug}.jpg" alt="{title}" loading="lazy" width="800" height="450" />
      </picture>

      <h2>Quick Verdict</h2>
      <p>QUICK VERDICT HERE.</p>

      <!-- Specs Table -->
      <h2>Specs at a Glance</h2>
      <table class="specs-table">
        <tbody>
          <tr><th>Spec 1</th><td>Value</td></tr>
          <tr><th>Spec 2</th><td>Value</td></tr>
          <tr><th>Spec 3</th><td>Value</td></tr>
          <tr><th>Price</th><td>X RON / $X</td></tr>
        </tbody>
      </table>

      <!-- Pros & Cons -->
      <div class="pros-cons">
        <div class="pros">
          <h3>Pros</h3>
          <ul>
            <li>Pro 1</li>
            <li>Pro 2</li>
            <li>Pro 3</li>
          </ul>
        </div>
        <div class="cons">
          <h3>Cons</h3>
          <ul>
            <li>Con 1</li>
            <li>Con 2</li>
          </ul>
        </div>
      </div>

      <!-- Review body -->
      <h2>Full Review</h2>
      <p>WRITE FULL REVIEW HERE.</p>

      <!-- Affiliate CTA -->
      <div class="cta-box">
        <p>Ready to buy? Check the latest price below:</p>
        <a href="{{PRODUCT_SLUG}}"
           target="_blank"
           rel="nofollow noopener noreferrer"
           class="btn-affiliate">
          View Price on eMAG &rarr;
        </a>
      </div>

    </article>
  </main>

  <footer>
    <p>
      &copy; {date.today().year} TechPicks &middot;
      <a href="../about.html">About</a> &middot;
      <a href="../feed.xml">RSS</a>
    </p>
    <p class="disclaimer">
      Some links are affiliate links. We may earn a commission at no extra cost to you.
    </p>
  </footer>
</body>
</html>
"""
    article_path.write_text(html)
    print(f"Created: {article_path}")

    # Update articles.json
    manifest_path = ROOT / "articles.json"
    articles = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    articles.insert(0, {
        "slug": slug,
        "title": title,
        "description": "WRITE DESCRIPTION HERE",
        "category": category,
        "published": today,
        "updated": today,
        "products": ["PRODUCT_SLUG"],
        "rating": 4.5
    })
    manifest_path.write_text(json.dumps(articles, indent=2))
    print(f"Updated: {manifest_path}")
    print(f"\nNext steps:")
    print(f"  1. Fill in the article content in: articles/{slug}.html")
    print(f"  2. Replace PRODUCT_SLUG with the real ProfitShare product slug")
    print(f"  3. Update description in both articles/{slug}.html and articles.json")
    print(f"  4. git add . && git commit -m 'Add article: {title}' && git push")

if __name__ == "__main__":
    main()
