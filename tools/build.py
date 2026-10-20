#!/usr/bin/env python3
"""Build the Better Forever demo: a style picker at / plus five full copies of the site.

Run from the repo root:  python3 tools/build.py

  /               style picker (site/index.html)
  /classic/       the original build            (tools/classic.py,   css/classic.css)
  /editorial/     serif magazine remodel        (tools/editorial.py, css/editorial.css)
  /bold/          poster / neo-brutalist        (editorial markup +  css/bold.css)
  /soft/          calm rounded wellness         (editorial markup +  css/soft.css)
  /noir/          black cinematic dark mode     (editorial markup +  css/noir.css)

Shared assets (img, fonts, js) live at the site root. Once a style is chosen, delete the
others and move the winner to the root (set PREFIX to "" in its module and drop picker.css).
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classic
import editorial

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"
DEMO = True
SITE_URL = "https://betterforever.ca"

STYLES = [
    dict(key="classic", mod=classic, css=["/css/classic.css"], theme="theme-classic",
         name="Classic", blurb="The original build. Rounded cards, all-caps Montserrat, a full-width photo hero.",
         feel=["Familiar", "Rounded", "Corporate-friendly"]),
    dict(key="editorial", mod=editorial, css=["/css/editorial.css"], theme="theme-editorial",
         name="Editorial", blurb="Magazine feel. Big serif headlines, thin rules, an arched photo and numbered lists.",
         feel=["Serif", "Refined", "Premium"]),
    dict(key="bold", mod=editorial, css=["/css/editorial.css", "/css/bold.css"], theme="theme-bold",
         name="Bold", blurb="Poster energy. Giant type, hard borders, offset shadows and highlighter marks.",
         feel=["Loud", "High contrast", "Athletic"]),
    dict(key="soft", mod=editorial, css=["/css/editorial.css", "/css/soft.css"], theme="theme-soft",
         name="Soft", blurb="Calm and welcoming. Centred layout, floating pill nav, big rounded cards, gentle shadows.",
         feel=["Calming", "Rounded", "Wellness"]),
    dict(key="noir", mod=editorial, css=["/css/editorial.css", "/css/noir.css"], theme="theme-noir",
         name="Noir", blurb="Black and cinematic. A full-bleed photo hero, glowing brand-green accents and glass cards.",
         feel=["Dark mode", "Cinematic", "Premium"]),
]


def build_picker():
    cards = []
    for i, s in enumerate(STYLES, 1):
        feel = "".join(f"<span>{html.escape(f)}</span>" for f in s["feel"])
        cards.append(f"""<a class="pk-card" href="/{s['key']}/">
      <div class="pk-shot"><img src="/img/previews/{s['key']}.jpg" width="1200" height="750" alt="Preview of the {s['name']} style home page" loading="{'eager' if i < 3 else 'lazy'}" decoding="async"><span class="pk-num">{i}</span></div>
      <div class="pk-body"><h2>{s['name']}</h2><p>{html.escape(s['blurb'])}</p><div class="pk-feel">{feel}</div><span class="pk-go">View this style &rarr;</span></div>
    </a>""")
    robots = '<meta name="robots" content="noindex, nofollow">\n' if DEMO else ""
    doc = f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pick a style | Better Forever website options</title>
<meta name="description" content="Five design directions for the Better Forever website. Pick the one you like.">
{robots}<meta name="theme-color" content="#005745">
<link rel="icon" type="image/png" href="/img/logo.png">
<link rel="preload" href="/fonts/fraunces-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/editorial.css">
<link rel="stylesheet" href="/css/picker.css">
</head>
<body class="pk">
<div class="pk-wrap">
  <div class="pk-top">
    <span class="pk-brand"><img src="/img/logo.png" width="44" height="51" alt="">Better Forever</span>
    <span class="pk-tag">Website design options</span>
  </div>
  <header class="pk-hero">
    <h1>Pick the style that <em>feels like you.</em></h1>
    <p>Five complete versions of the same site, same content, same colours, five different looks. Click one to explore every page, then use the &ldquo;All styles&rdquo; button at the bottom left to come back and compare.</p>
  </header>
  <main class="pk-grid">
    {''.join(cards)}
  </main>
  <div class="pk-note">
    <p><strong>What stays the same:</strong> brand colours, copy, team, booking flow and contact details. Only layout, typography and visual treatment change.</p>
    <p><strong>What happens next:</strong> once you choose, the other four get removed and the winner moves to the main address. Easy to tweak further after that.</p>
  </div>
  <p class="pk-credit">Built by <a href="https://stackwell.digital" target="_blank" rel="noopener">stackwell.digital</a></p>
</div>
</body>
</html>
"""
    (OUT / "index.html").write_text(doc, encoding="utf-8")


def clean_old():
    """Remove pages from earlier single-style builds that used to sit at the site root."""
    import shutil
    for d in ("pain", "perform", "young-forever", "team", "contact", "book"):
        shutil.rmtree(OUT / d, ignore_errors=True)
    for f in ("404.html", "sitemap.xml"):
        (OUT / f).unlink(missing_ok=True)
    for key in [s["key"] for s in STYLES] + ["studio"]:
        shutil.rmtree(OUT / key, ignore_errors=True)


def build_404():
    robots = '<meta name="robots" content="noindex, nofollow">\n' if DEMO else ""
    (OUT / "404.html").write_text(f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | Better Forever</title>
{robots}<link rel="stylesheet" href="/css/editorial.css"><link rel="stylesheet" href="/css/picker.css"></head>
<body class="pk"><div class="pk-wrap"><header class="pk-hero" style="padding-top:4rem"><h1>That page <em>doesn't exist.</em></h1>
<p><a href="/">Back to the style picker</a></p></header></div></body></html>
""", encoding="utf-8")


if __name__ == "__main__":
    clean_old()
    total = 0
    for s in STYLES:
        mod = s["mod"]
        mod.DEMO = DEMO
        urls = mod.build_all("/" + s["key"], s["css"], s["theme"])
        total += len(urls)
    build_picker()
    build_404()
    (OUT / "robots.txt").write_text(
        "User-agent: *\nDisallow: /\n" if DEMO else "User-agent: *\nAllow: /\n", encoding="utf-8")
    print(f"built picker + {len(STYLES)} styles ({total} pages) into {OUT} (DEMO={DEMO})")
