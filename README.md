# peterramaldes.com

A minimal blog. No JS, no analytics, no tracking — just Markdown in, static HTML out.

## Writing a post

Add a file to `posts/`, e.g. `posts/my-post.md`:

```markdown
---
title: My Post
date: 2026-01-01
description: One-sentence summary for the post list.
---

Content goes here, in Markdown. `## Headings` become table-of-contents entries.
```

Commit and push to `main` — GitHub Actions builds the site (`build.py`) and deploys it
to GitHub Pages automatically. Nothing to run locally.

## Local preview

```
pip install -r requirements.txt
python build.py
python -m http.server -d _site 8000
```
