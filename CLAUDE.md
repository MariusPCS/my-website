# TechPicks — Project Guide for Claude Code

## What This Project Is
A **premium, modern** automated **bilingual (Romanian + English)** tech review blog hosted on GitHub Pages, monetized via ProfitShare.ro affiliate links. Every push to `main` triggers a full pipeline that validates links, fetches fresh affiliate data, and deploys the site.

The look and feel must read as a polished, trustworthy editorial product — on par with sites like The Verge, Wirecutter, or Linear's marketing pages — never as a template or hobby blog. Visual quality is a first-class requirement, not an afterthought.

**Live URL:** `https://mariuspcs.github.io/my-website/`

---

## Language: Romanian + English (REQUIRED)

The site must be available in **both Romanian (`ro`) and English (`en`)**. ProfitShare.ro is a Romanian affiliate network, so Romanian is the primary market; English broadens reach.

**Structure: a `/ro/` mirror.** English lives at the site root; Romanian mirrors it under `ro/`:
| English (root) | Romanian (`ro/` mirror) |
|----------------|--------------------------|
| `index.html` | `ro/index.html` |
| `about.html` | `ro/about.html` |
| `articles/<slug>.html` | `ro/articles/<slug>.html` |

- A **language switcher** (`.lang-switch` in the header) toggles EN ↔ RO on every page.
- Set the correct `<html lang="ro">` or `<html lang="en">` per page.
- Add `hreflang` alternates in every page's `<head>` so Google serves the right language:
  ```html
  <link rel="alternate" hreflang="en" href="https://mariuspcs.github.io/my-website/articles/<slug>.html" />
  <link rel="alternate" hreflang="ro" href="https://mariuspcs.github.io/my-website/ro/articles/<slug>.html" />
  <link rel="alternate" hreflang="x-default" href="https://mariuspcs.github.io/my-website/ro/articles/<slug>.html" />
  ```
- Relative paths differ by depth: root article → `../style.css`; `ro/articles/` → `../../style.css`.
- `articles.json` carries both `title`/`title_ro` and `description`/`description_ro` fields.
- Affiliate CTAs are translated ("View on eMAG" / "Vezi pe eMAG") but use the **same** `{{PRODUCT_SLUG}}` placeholder in both versions.

---

## Development Workflow: Use Claude Skills

When building or improving the site, **prefer Claude Code skills over ad-hoc work**:

- **Web design / UI work** — use a web design skill (or the `run` skill to launch and preview the site) to iterate on layout, visuals, and responsiveness rather than hand-tweaking CSS blindly. Always preview the rendered result before committing.
- **`code-review`** — run before pushing significant changes to catch bugs and cleanups.
- **`simplify`** — tidy up CSS/HTML/scripts for reuse and clarity.
- **`security-review`** — run when touching the affiliate pipeline, secrets handling, or workflows.
- **`verify`** — confirm a change actually renders/works in the browser before declaring it done.

Treat design and review skills as the default path for non-trivial visual or structural changes.

---

## Design System — Premium Modern Look (REQUIRED)

Every page and component must meet this bar. When in doubt, choose restraint, whitespace, and consistency over decoration.

### Core principles
- **Generous whitespace** — let content breathe; never cram. Whitespace signals premium.
- **Restraint** — one accent color, a tight type scale, consistent spacing. No rainbow palettes, no clip-art, no random emoji as icons.
- **Consistency** — every spacing, radius, shadow, and color comes from the design tokens below. No one-off magic numbers.
- **Depth, subtly** — soft, low-opacity shadows and hairline borders for elevation. No heavy drop shadows or harsh 1px black lines.
- **Motion with purpose** — smooth, fast micro-interactions (150–250ms ease) on hover/focus. Never gratuitous animation.

### Design tokens (single source of truth in `style.css`, defined on `:root`)
```css
/* Color — refined neutral base + a single confident accent */
--color-bg: #ffffff;
--color-surface: #f7f8fa;      /* cards, subtle fills */
--color-border: #e8eaed;        /* hairline borders */
--color-text: #0f1115;          /* near-black, not pure #000 */
--color-muted: #5f6571;         /* secondary text */
--color-accent: #4f46e5;        /* indigo — confident, modern */
--color-accent-hover: #4338ca;

/* Typography */
--font-sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
--font-display: "Inter", system-ui, sans-serif;   /* tighter tracking for headings */

/* Spacing scale (4px base) — use ONLY these */
--space-1: 0.25rem; --space-2: 0.5rem; --space-3: 0.75rem;
--space-4: 1rem;    --space-6: 1.5rem; --space-8: 2rem;
--space-12: 3rem;   --space-16: 4rem;  --space-24: 6rem;

/* Radius & elevation */
--radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --radius-full: 999px;
--shadow-sm: 0 1px 2px rgba(15,17,21,0.04), 0 1px 3px rgba(15,17,21,0.06);
--shadow-md: 0 4px 12px rgba(15,17,21,0.06), 0 2px 4px rgba(15,17,21,0.04);
--shadow-lg: 0 12px 32px rgba(15,17,21,0.10);
```

### Typography rules
- Headings use a tight letter-spacing (`-0.02em` to `-0.03em`) and strong weight (700–800).
- Body text: 1.0625rem (17px), `line-height: 1.7`, max line length ~70ch for readability.
- Use a fluid scale for hero/H1: `clamp(2rem, 5vw, 3.25rem)`.
- Load **Inter** (or a comparable modern grotesque) via `<link rel="preconnect">` + `font-display: swap`; system-ui is the fallback.

### Dark mode (REQUIRED)
Support `@media (prefers-color-scheme: dark)` with a parallel token set (dark surface `#0f1115`, elevated `#1a1d23`, text `#e6e8eb`). The toggle is automatic; no flash of wrong theme.

### Component standards
- **Cards** — `--radius-md`, `--shadow-sm` at rest, lift to `--shadow-md` + `translateY(-2px)` on hover, hairline border. Image fills top with consistent aspect ratio (16:9).
- **Buttons / affiliate CTAs** — solid accent fill, `--radius-sm`, confident padding (`0.75rem 1.5rem`), subtle hover darken + lift, visible `:focus-visible` ring (accessibility).
- **Header** — sticky, translucent with `backdrop-filter: blur(12px)`, hairline bottom border, logo wordmark left, nav + language switcher right.
- **Images** — always real, high-resolution, consistent aspect ratios. Never stretched or low-res. Rounded corners (`--radius-md`).
- **Hero** — large, confident headline with generous vertical padding (`--space-24`), optional subtle gradient mesh background.

### Hard rules (do NOT violate)
- No pure black (`#000`) or pure-saturated colors for large areas.
- No more than one accent color in active use.
- No inline styles for layout — everything flows through `style.css` tokens.
- Every interactive element has a visible focus state and meets WCAG AA contrast (≥4.5:1 for text).
- Mobile-first and fully responsive; test at 360px, 768px, and 1280px widths.

### Verification
After any visual change, use the `run`/`verify` skills to preview the rendered site and confirm it looks premium on both mobile and desktop, in light and dark mode, before committing. Optionally run a Lighthouse pass — target 95+ on Performance, Accessibility, Best Practices, SEO.

---

## How to Publish a New Article

Ask Claude: *"Write an article about [topic]"* — Claude will:

1. Run `python scripts/new-article.py "Article Title" category` to scaffold the file
2. Write the article content in `articles/<slug>.html`
3. Update the description in `articles.json`
4. Run `git add . && git commit -m "Add article: Title" && git push`

The site deploys automatically in ~2 minutes with fresh, validated affiliate links.

**Categories:** `laptops`, `phones`, `tablets`, `peripherals`, `smart-home`, `audio`

---

## Affiliate Link System

### Adding links in articles
Use `{{PRODUCT_SLUG}}` placeholders — never hardcode tracking URLs:
```html
<a href="{{EMAG_HOME}}" target="_blank" rel="nofollow noopener noreferrer" class="btn-affiliate">
  View on eMAG →
</a>
```

### How slugs are resolved
`fetch-products.py` pulls the live product catalog from ProfitShare API and outputs `products.json` (gitignored). `inject-links.py` replaces all `{{SLUG}}` placeholders before deploy.

### Common slugs
- `{{EMAG_HOME}}` — eMAG homepage affiliate link (always available)
- `{{ALTEX_HOME}}` — Altex homepage affiliate link
- Product-specific slugs are fetched from the API and vary

### Required link attributes (always)
```
target="_blank"
rel="nofollow noopener noreferrer"
class="btn-affiliate"
```

---

## GitHub Secrets Required

| Secret | Purpose |
|--------|---------|
| `PROFITSHARE_API_KEY` | ProfitShare API authentication |
| `PROFITSHARE_AFF_CODE` | Your affiliate code for tracking URLs |

Set at: GitHub repo → Settings → Secrets and variables → Actions

**Never commit these values to the repo.**

---

## Pipeline (runs on every push to `main`)

1. `audit-links.py` — validates all existing affiliate links, replaces stale ones
2. `check-internal.py` — verifies all internal HTML links resolve (fails build on broken links)
3. `fetch-products.py` — fetches product catalog from ProfitShare API (falls back to cache if API is down)
4. `inject-links.py` — replaces `{{SLUG}}` placeholders with live tracking URLs
5. `optimize-images.py` — converts PNG/JPG to WebP, resizes if > 1200px
6. `generate-meta.py` — regenerates `sitemap.xml`, `feed.xml`, and homepage article grid from `articles.json`
7. Deploy to GitHub Pages

**Weekly audit:** `.github/workflows/audit.yml` runs every Monday at 08:00 UTC, audits and auto-commits any link updates.

---

## File Structure

```
/
├── index.html              # Homepage (article grid auto-generated)
├── about.html              # About page
├── 404.html                # Custom error page
├── style.css               # All styles — single file
├── robots.txt              # Crawler config
├── sitemap.xml             # Auto-generated by generate-meta.py
├── feed.xml                # Auto-generated RSS by generate-meta.py
├── articles.json           # Master article manifest — source of truth
├── articles/               # English articles (one .html per article)
├── ro/                     # Romanian mirror
│   ├── index.html
│   ├── about.html
│   └── articles/           # Romanian articles
├── assets/images/          # WebP images (originals gitignored)
├── scripts/                # Python pipeline scripts
└── .github/workflows/      # deploy.yml + audit.yml
```

---

## articles.json Schema

```json
{
  "slug": "kebab-case-url-slug",
  "title": "Full Article Title (English)",
  "title_ro": "Titlul articolului (Română)",
  "description": "One sentence, max 160 chars (English) — meta tags, cards, RSS",
  "description_ro": "O propoziție, max 160 caractere (Română)",
  "category": "laptops",
  "published": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "products": ["EMAG_HOME"],
  "rating": 4.5
}
```

---

## SEO Checklist (per article)

- [ ] `<title>` includes keyword + " | TechPicks", under 60 chars
- [ ] `<meta name="description">` is unique, under 160 chars, includes keyword
- [ ] `<link rel="canonical">` points to the correct URL
- [ ] `og:title`, `og:description`, `og:image`, `og:url` all set
- [ ] JSON-LD `Review` or `Article` schema present
- [ ] `AggregateRating` included if article is a review
- [ ] All images have `alt` attributes and `loading="lazy"`
- [ ] Breadcrumb navigation present
- [ ] `hreflang` alternates for both `ro` and `en` versions + `x-default`
- [ ] Both language versions published (`articles/ro/<slug>.html` and `articles/<slug>.html`)

---

## Images

- Place source images in `assets/images/` named `<article-slug>.jpg`
- `optimize-images.py` converts to WebP automatically on deploy
- Always use `<picture>` with WebP + JPG fallback:
```html
<picture>
  <source srcset="assets/images/<slug>.webp" type="image/webp" />
  <img src="assets/images/<slug>.jpg" alt="..." loading="lazy" width="800" height="450" />
</picture>
```
- Target size: 800×450px, under 150KB after optimization

---

## Deployment

Push to `main` → GitHub Actions → live in ~2 minutes.

GitHub Pages source must be set to **GitHub Actions**:
Repo → Settings → Pages → Source → GitHub Actions
