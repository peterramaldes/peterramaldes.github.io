#!/usr/bin/env python3
"""Builds the static site from Markdown sources in posts/ and about.md
into the _site/ output directory. Run: python build.py"""

import datetime
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
POSTS_DIR = ROOT / "posts"
TEMPLATE = (ROOT / "templates" / "base.html").read_text()
YEAR = datetime.date.today().year


def parse_front_matter(text):
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return {}, text
    meta = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        key, _, value = lines[i].partition(":")
        meta[key.strip()] = value.strip()
        i += 1
    body = "\n".join(lines[i + 1:])
    return meta, body


def render_toc(tokens, depth=0):
    if not tokens:
        return ""
    items = []
    for token in tokens:
        children = render_toc(token["children"], depth + 1)
        items.append(f'<li><a href="#{token["id"]}">{token["name"]}</a>{children}</li>')
    return "<ul>" + "".join(items) + "</ul>"


def render_page(title, description, content_html, body_class=""):
    return TEMPLATE.format(
        title=title,
        description=description,
        content=content_html,
        year=YEAR,
        body_class=body_class,
    )


def write(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)


def build_post(md_path):
    meta, body = parse_front_matter(md_path.read_text())
    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    content_html = md.convert(body)
    toc_html = render_toc(md.toc_tokens)

    title = meta.get("title", md_path.stem)
    date = meta.get("date", "")
    description = meta.get("description", "")

    toc_block = f'<nav class="toc side"><p class="toc-title">Contents</p>{toc_html}</nav>' if toc_html else ""

    page_content = f"""
<div class="post-layout">
  <article>
    <h1>{title}</h1>
    <p class="meta">{date}</p>
    {content_html}
  </article>
  {toc_block}
</div>
"""
    html = render_page(title, description, page_content, body_class="post")
    slug = md_path.stem
    write(OUT / "posts" / slug / "index.html", html)
    return {"title": title, "date": date, "description": description, "slug": slug}


def build_about():
    about_path = ROOT / "about.md"
    meta, body = parse_front_matter(about_path.read_text())
    md = markdown.Markdown(extensions=["extra"])
    content_html = md.convert(body)
    title = meta.get("title", "About")
    description = meta.get("description", "")
    page_content = f"<article>\n<h1>{title}</h1>\n{content_html}\n</article>\n"
    html = render_page(title, description, page_content)
    write(OUT / "about" / "index.html", html)


def build_index(posts):
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    items = []
    for p in posts_sorted:
        items.append(f"""
<li>
  <a class="title" href="/posts/{p['slug']}/">{p['title']}</a>
  <span class="date">{p['date']}</span>
  <p class="desc">{p['description']}</p>
</li>
""")
    list_html = '<ul class="post-list">' + "".join(items) + "</ul>" if items else "<p>No posts yet.</p>"
    page_content = f"<h1>Peter A. Ramaldes</h1>\n{list_html}"
    html = render_page("Peter A. Ramaldes", "Notes on software and things I'm building.", page_content)
    write(OUT / "index.html", html)


def copy_static():
    dest = OUT / "static"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ROOT / "static", dest)
    cname = ROOT / "CNAME"
    if cname.exists():
        shutil.copy(cname, OUT / "CNAME")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    posts = [build_post(p) for p in sorted(POSTS_DIR.glob("*.md"))]
    build_about()
    build_index(posts)
    copy_static()
    print(f"Built {len(posts)} post(s) into {OUT}")


if __name__ == "__main__":
    main()
