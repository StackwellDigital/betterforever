#!/usr/bin/env python3
"""Regenerate the picker thumbnails (needs: pip install playwright && playwright install chromium).
Run after tools/build.py:  python3 tools/previews.py"""
import functools, http.server, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = SITE / "img" / "previews"
OUT.mkdir(parents=True, exist_ok=True)

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(SITE)))
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    for key in ("classic", "editorial", "bold", "soft", "studio"):
        pg.goto(f"http://127.0.0.1:{port}/{key}/")
        pg.evaluate("document.querySelectorAll('.picker-chip,.float-book').forEach(e=>e.remove())")
        pg.wait_for_timeout(700)
        pg.screenshot(path=str(OUT / f"{key}.jpg"), type="jpeg", quality=82,
                      clip={"x": 0, "y": 0, "width": 1440, "height": 900})
        print("shot", key)
    b.close()
