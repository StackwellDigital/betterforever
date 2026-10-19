# Better Forever website

Static rebuild of the Better Forever (Langley, BC) site. Plain HTML, CSS and a little vanilla JS. No framework, no build step on the host. Brand colours, fonts, copy and contact details come from the client's existing preview site.

## Layout

```
site/            <- deploy this folder (CF Pages "build output directory")
  index.html, pain/, perform/, young-forever/, team/, contact/, book/, 404.html
  css/styles.css          brand tokens live in :root at the top
  js/config.js            Jane App URLs + form endpoint (the only file to edit for booking)
  js/main.js              nav, carousel, Jane link wiring, forms
  img/ fonts/             logo, self-hosted Montserrat + Open Sans (variable woff2)
  _headers                security headers + caching (Cloudflare Pages format)
tools/build.py   <- generates every HTML page; all copy and the shared header/footer live here
```

Pages are generated, so **edit `tools/build.py` and re-run it, not the HTML**:

```
python3 tools/build.py
```

Needs only Python 3. It rewrites everything under `site/` except css, js, img, fonts and `_headers`.

## Deploy to Cloudflare Pages (demo)

Git integration: Pages -> Create project -> connect the repo, then set

- Framework preset: None
- Build command: *(leave empty)*
- Build output directory: `site`

Or direct upload with no git: `npx wrangler pages deploy site --project-name betterforever-demo`

## Before this can be used for real

1. **Photos.** Two image files were not copied over. Save them from the existing preview into `site/img/` using these exact names:
   - `joel-and-clients.avif` (hero background; without it the hero is a plain green gradient)
   - `joel.avif` (Joel's portrait on /team; without it his card shows initials like the others)
2. **Jane App.** Open `site/js/config.js` and paste the clinic's Jane URL into `jane.general`, plus per-practitioner URLs if they have them. Until then every Book Now button lands on the on-site `/book/` page so nothing is a dead link.
3. **Inquiry forms.** Set `inquiryEndpoint` in `config.js` (Formspree, a Pages Function, etc). Until then the forms open the visitor's email app addressed to admin@betterforever.ca.
4. **Go live.** In `tools/build.py` set `DEMO = False` and re-run it. While `DEMO = True` every page has `noindex` and `robots.txt` blocks all crawlers, so the demo cannot get indexed. Going live also writes `sitemap.xml` using `SITE_URL`.
5. **Hours** were "to be confirmed" on the client's preview, so they are left off. Add them (and `openingHoursSpecification` in the JSON-LD) once known.
6. The preview's footer social icons pointed at `#`. They are omitted here; add real links when the client has them.

## Compliance flag for the client

The copy includes outcome claims, a money-back guarantee, success-rate figures, and named client testimonials. Regulated health professionals in BC (naturopathic doctors, chiropractors, kinesiologists) are bound by their college's advertising standards, which restrict testimonials and guarantees. The copy is carried over unchanged from the client's own draft, but they should confirm it with their colleges before launch.
