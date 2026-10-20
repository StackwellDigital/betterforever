#!/usr/bin/env python3
"""Build the Better Forever site into site/. Run from the repo root:  python3 tools/build.py

Page copy, header and footer live in tools/classic.py; styles in site/css/classic.css.
Set DEMO = False below at launch (removes noindex and opens robots.txt).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classic

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"
DEMO = True
SITE_URL = "https://betterforever.ca"


def build_404():
    robots = '<meta name="robots" content="noindex, nofollow">\n' if DEMO else ""
    (OUT / "404.html").write_text(f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | Better Forever</title>
{robots}<link rel="stylesheet" href="/css/classic.css"></head>
<body class="theme-classic"><main style="max-width:40rem;margin:6rem auto;padding:0 1.25rem">
<h1>That page doesn't exist.</h1><p><a href="/">Back to the home page</a></p></main></body></html>
""", encoding="utf-8")


if __name__ == "__main__":
    classic.DEMO = DEMO
    urls = classic.build_all("", ["/css/classic.css"], "theme-classic")
    build_404()
    (OUT / "robots.txt").write_text(
        "User-agent: *\nDisallow: /\n" if DEMO else f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8")
    if DEMO:
        (OUT / "sitemap.xml").unlink(missing_ok=True)
    else:
        items = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
        (OUT / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n',
            encoding="utf-8")
    print(f"built {len(urls)} pages into {OUT} (DEMO={DEMO})")
