# Project Overview

A simple HTML/CSS website that auto-deploys to GitHub Pages on every push to `main`.

## Structure

- `index.html` — main page
- `style.css` — all styles
- `.github/workflows/deploy.yml` — GitHub Actions deploy pipeline

## Deployment

Push to `main` → GitHub Actions runs → site is live at:
`https://<username>.github.io/<repo-name>/`

GitHub Pages must be configured to use **GitHub Actions** as the source:
Repo → Settings → Pages → Source → GitHub Actions

## Development

No build step. Edit HTML/CSS directly and push. The site deploys in ~1 minute.
