#!/usr/bin/env python3
"""Hydrate dist/index.html with all paginated posts so the home page is fully static.

blogr 0.5.1 hard-codes POSTS_PER_PAGE = 10 and renders the rest via a client-side
infinite-scroll JS that fetches dist/api/posts-page-N.json. With a small archive
(18 posts here) the dynamic load adds no value and can fail to surface tags if the
fetch never fires (e.g. user never scrolls). This script reads the page-N JSON
files blogr already generates and inlines them as the same static <article>
structure that the Tera template emits for page 1 — then disables the JS loader.

Run after `blogr build`.
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from textwrap import indent

DIST = Path(__file__).resolve().parent.parent / "dist"
INDEX = DIST / "index.html"
API = DIST / "api"

# Mirror blogr.toml [blog].base_url, with trailing slash stripped.
BASE_URL = "https://blog.gokuls.in"


def fmt_date(iso: str) -> str:
    # blogr serializes dates as RFC3339, e.g. "2020-02-06T00:00:00Z"
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%b %d, %Y")


def render_article(post: dict, post_id: int) -> str:
    md = post["metadata"]
    title = html.escape(md["title"])
    description = html.escape(md.get("description") or "")
    author = html.escape(md.get("author") or "")
    slug = md["slug"]
    tags = md.get("tags") or []
    reading_time = post.get("reading_time")
    content_html = post.get("content") or ""
    date_str = fmt_date(md["date"])
    is_external = post.get("is_external", False)
    post_url = post.get("post_url") or f"posts/{slug}.html"

    # Tag bubbles + tag links — match the Tera template's exact whitespace shape so
    # the static and hydrated articles are visually identical to a human reader.
    tag_bubbles = "".join(
        f'\n                    <span class="tag-bubble">{html.escape(t)}</span>\n                    '
        for t in tags
    )
    tag_links = ", \n                        ".join(
        f'<a href="{BASE_URL}/tags/{html.escape(t)}.html" class="tag-link">{html.escape(t)}</a>'
        for t in tags
    )
    tags_preview_block = (
        f'<div class="post-tags-preview">{tag_bubbles}\n                </div>'
        if tags
        else ""
    )
    tags_full_block = (
        f'<div class="post-tags-full">\n                        <span class="tags-label">tagged:</span>\n                        \n                        {tag_links}\n                        \n                    </div>'
        if tags
        else ""
    )

    if is_external:
        ext_url = html.escape(post_url)
        header_open = (
            f'<a href="{ext_url}" target="_blank" rel="noopener" class="post-entry-external-link" style="text-decoration: none; color: inherit; display: block;">\n'
            f'            <header class="post-entry-header">\n'
            f'                <h2 class="post-entry-title">{title} ↗</h2>'
        )
        header_close_extra = "</a>"
        permalink_html = f'<a href="{ext_url}" target="_blank" rel="noopener" class="permalink">external link ↗</a>'
    else:
        header_open = (
            f'<header class="post-entry-header" onclick="togglePost({post_id})">\n'
            f'                <h2 class="post-entry-title">{title}</h2>'
        )
        header_close_extra = ""
        permalink_html = (
            f'<a href="{BASE_URL}/{post_url}" class="permalink">permalink</a>'
        )

    return (
        f'        <article class="post-entry" data-post-id="{post_id}">\n'
        f'            <!-- Post Header -->\n'
        f'            {header_open}\n'
        f'            \n'
        f'                \n'
        f'                <div class="post-entry-meta">\n'
        f'                    <time class="post-date">{date_str}</time>\n'
        f'                    \n'
        f'                    \n'
        f'                    <span class="post-author">{author}</span>\n'
        f'                    \n'
        f'                    \n'
        f'                    \n'
        f'                    <span class="reading-time">{reading_time}min</span>\n'
        f'                    \n'
        f'                </div>\n\n'
        f'                <!-- Tags as artistic elements -->\n'
        f'                \n'
        f'                {tags_preview_block}\n'
        f'                \n\n'
        f'                <!-- Expand indicator -->\n'
        f'                <div class="expand-indicator">\n'
        f'                    <span class="expand-text">read</span>\n'
        f'                    <span class="expand-arrow">↓</span>\n'
        f'                </div>\n'
        f'            </header>\n'
        f'            {header_close_extra}\n\n'
        f'            <!-- Expandable Content -->\n'
        f'            <div class="post-entry-content" id="post-content-{post_id}">\n'
        f'                \n'
        f'                <div class="post-description">\n'
        f'                    {description}\n'
        f'                </div>\n'
        f'                \n'
        f'                \n'
        f'                <div class="post-full-content">\n'
        f'                    {content_html}\n'
        f'                </div>\n\n'
        f'                <!-- Post Footer with full tags -->\n'
        f'                <footer class="post-entry-footer">\n'
        f'                    \n'
        f'                    {tags_full_block}\n'
        f'                    \n\n'
        f'                    <div class="post-actions">\n'
        f'                        \n'
        f'                        {permalink_html}\n'
        f'                        \n'
        f'                        <button class="collapse-btn" onclick="togglePost({post_id})">collapse</button>\n'
        f'                    </div>\n'
        f'                </footer>\n'
        f'            </div>\n'
        f'        </article>\n'
        f'        '
    )


def main() -> int:
    if not INDEX.exists():
        print(f"hydrate-index: {INDEX} not found (did `blogr build` run?)", file=sys.stderr)
        return 1

    page_files = sorted(API.glob("posts-page-*.json"), key=lambda p: int(re.search(r"(\d+)", p.name).group(1)))
    extra_pages = [p for p in page_files if int(re.search(r"(\d+)", p.name).group(1)) >= 2]
    if not extra_pages:
        print("hydrate-index: only one page of posts, nothing to inline")
        return 0

    # Count already-rendered articles to continue post-id numbering.
    html_text = INDEX.read_text()
    existing_articles = len(re.findall(r'<article class="post-entry"', html_text))
    next_id = existing_articles + 1

    rendered_articles: list[str] = []
    for page_path in extra_pages:
        data = json.loads(page_path.read_text())
        for post in data.get("posts", []):
            rendered_articles.append(render_article(post, next_id))
            next_id += 1

    if not rendered_articles:
        print("hydrate-index: no posts in page-2+ JSON, nothing to inline")
        return 0

    insertion = "\n".join(rendered_articles)

    # The Tera template closes the posts-container with the {% else %} branch or
    # `</div>` immediately after the for-loop. We insert right before the empty-state
    # fallback (which renders only when posts is empty — so it's always present in
    # the static output as dead branches around it). Concretely: find the closing
    # `</div>` of posts-container by anchoring on the loading-indicator that follows.
    marker = '<!-- Loading indicator for infinite scroll -->'
    if marker not in html_text:
        print(f"hydrate-index: marker {marker!r} not found in index.html", file=sys.stderr)
        return 2

    # Insert articles + the closing </div> of posts-container before the marker.
    # blogr's emitted output places `</div>` of .posts-container right before this
    # marker, so we splice articles just before that closing `</div>`.
    before, after = html_text.split(marker, 1)
    # Find the last `</div>` in `before` (which closes posts-container).
    close_idx = before.rfind("</div>")
    if close_idx == -1:
        print("hydrate-index: could not find posts-container closing </div>", file=sys.stderr)
        return 3
    new_before = before[:close_idx] + insertion + "\n    " + before[close_idx:]

    # Disable the client-side loader: with all posts already inlined, there's nothing
    # left to fetch. Setting hasMorePosts=false also hides the end-of-posts banner
    # cleanly (it's display:none until JS toggles it).
    new_html = new_before + marker + after
    new_html = re.sub(r"let hasMorePosts = true;", "let hasMorePosts = false;", new_html, count=1)

    INDEX.write_text(new_html)
    print(f"hydrate-index: inlined {len(rendered_articles)} post(s) into index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
