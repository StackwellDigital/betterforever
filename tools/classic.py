#!/usr/bin/env python3
"""Static site generator for Better Forever (Langley, BC).

Run from the repo root:  python3 tools/build.py
Writes plain HTML into ./site (no build step needed on Cloudflare Pages).
All copy comes from the client's existing preview site; nothing is invented.
"""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"

# ---------------------------------------------------------------- settings
SITE_URL = "https://www.betterforever.ca"   # used for canonical + sitemap only
PREFIX = ""                              # site root
CSS = []                                 # stylesheet hrefs for this style
THEME = ""                               # body class for this style
DEMO = True                              # True = noindex everywhere. Flip to False at launch.
NAME = "Better Forever"
TAGLINE = "Find Your Better"
PHONE_DISPLAY = "778-766-5083"
PHONE_TEL = "+17787665083"
EMAIL = "info@betterforever.ca"
ADDR_STREET = "#101 - 20086 92A Avenue"
ADDR_CITY = "Langley"
ADDR_REGION = "BC"
ADDR_POSTAL = "V1M 3A4"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=" + \
    "%23101+-+20086+92A+Avenue%2C+Langley+BC+V1M+3A4"
DESCRIPTION = ("Better Forever is a functional health, performance, and pain "
               "resolution center in Langley, BC. Find your better.")

e = html.escape


# ---------------------------------------------------------------- team data
TEAM = [
    {
        "key": "berghamer", "initials": "JB", "photo": "/img/berghamer.jpg",
        "name": "Dr. Jonathon Berghamer",
        "role": "Naturopathic Doctor - Co-Founder of Better Forever",
        "short": "Book with Dr. Berghamer",
        "bio": [
            "Dr. Berghamer received his Honours Bachelor of Science in Genetics and Molecular Biology at the University of Guelph. He later completed his Doctor of Naturopathic Medicine at the Boucher Institute of Naturopathic Medicine.",
            "Health is not an end point but rather a journey of self-discovery, knowledge and wisdom. Health is as simple as it is complex and each individual has specific needs as well as obstacles. Integrating science and nature, Dr. Berghamer endeavours to create relationships with patients that empower them with knowledge such that their health goals are not only achieved but sustained.",
            "As a naturopathic doctor and Co-Founder of Better Forever, Dr. Berghamer has expertise in physical medicine, sport medicine, genomics and integrative pain management. By combining the principles of naturopathic medicine and science, Dr. Berghamer has created a unique approach to pain management and longevity.",
            "Having been involved in sports from a young age, Dr. Berghamer well recognizes the benefits of physical fitness but also the challenges that come with being injured. But the reality is that most injuries occur outside of sport. When we are limited in what we love to do, whether it be long walks or power lifting, it has significant impact on our health and mental well-being. Understanding the complexity and mechanisms of pain is critical in order to alleviate its burden.",
            "While it is often necessary to identify and treat pain generators directly, vibrant health is not only defined as being pain-free. Everyone deserves to live fulfilling lives that are not only free of pain but are thriving in health. Longevity should be measured by both quantity and quality.",
            "Dr. Berghamer has developed significant clinical experience working with a large variety of musculoskeletal conditions, injuries and pain, as well as traumatic brain injuries and concussions, hormone optimization, chronic systemic and digestive infections, and longevity optimization through genetic assessment and interpretation. Dr. Berghamer incorporates exercise, epigenetics, nutrition and manual therapies to help patients attain their health goals.",
            "In the context of pain, Dr. Berghamer is one of the most skilled practitioners in the field of regenerative medicine, employing prolotherapy, neural therapy, platelet rich plasma therapy, bio-oxidative therapy, acupuncture and manual therapies in pain management and resolution. He employs a combination of hands-on techniques with individualized assessment programs to help patients live the lives they love.",
            "Dr. Berghamer works with the integrated team at Better Forever. Weekends are often spent teaching other practitioners prolotherapy, bio-oxidative therapies, PRP and ultrasound.",
        ],
    },
    {
        "key": "kawamoto", "initials": "KK",
        "name": "Dr. Kyle Kawamoto",
        "role": "Chiropractor and Naturopathic Doctor",
        "short": "Book with Dr. Kawamoto",
        "bio": [
            "Dr. Kyle Kawamoto is a licensed chiropractor and naturopathic doctor. Following his athletic career, he spent four years working in biomechanics and performance, helping athletes and rehabilitation patients optimize movement and recovery. He earned his Doctor of Chiropractic degree from the University of Western States and his Doctor of Naturopathic Medicine degree from the National University of Health Sciences.",
            "Dr. Kawamoto takes a performance-driven, evidence-informed approach, combining his background in chiropractic care, biomechanics, and naturopathic medicine. He focuses on improving movement efficiency, reducing injury risk, and supporting recovery.",
            "He has a strong interest in regenerative medicine, longevity, and hormone health, and has experience working with athletes at the NFL, CFL, NHL, and Olympic levels. His approach emphasizes optimizing biomechanics, supporting tissue health, and helping individuals perform and function at a high level while promoting long-term wellness.",
        ],
    },
    {
        "key": "joel", "initials": "JM", "photo": "/img/joel.avif",
        "name": "Joel McCain",
        "role": "Head Trainer - Creator of CORE4 & CORE4+",
        "short": "Book with Joel",
        "bio": [
            "Joel has trained 4 World Record holding strength athletes as well as numerous national and provincial record holders. Over the last 15 years as a strength coach he has trained collegiate, professional, and Olympic athletes in over 15 sports.",
            "As a strength athlete himself, he has broken national records in 4 different weight classes, all after sustaining a head and spine injury where he was told by multiple doctors he would never lift again.",
            "It was through his own frustrating experience navigating the medical system that he discovered the desperate need for a better system to help those with injuries and chronic pain. Through collaboration with other key members of the Better Forever team, he developed the CORE4 system that has helped hundreds of people achieve pain free movement with an over 90% success rate, regardless of how many times they had failed to achieve improvement beforehand.",
            "Joel has a life-long desire for the incredible benefits of movement. He has competed in over 10 sports, has a huge passion for off-road and racing motorsports. Always looking for the next challenge, he is currently training for a master’s track meet despite having no previous experience as a sprinter.",
        ],
    },
    {
        "key": "cam", "initials": "CB",
        "name": "Cam Bennett",
        "role": "Strength and Performance Coach",
        "short": "Book with Cam",
        "bio": [
            "Cam Bennett is a Strength and Performance Coach with more than a decade of coaching experience and over two decades of strength training behind him. His path into coaching began through his own experience with competitive powerlifting, injuries, and the process of learning how to rebuild his body and continue performing at a high level.",
            "Cam has since worked with hundreds of clients across a wide range of ages, abilities, and goals. He has coached powerlifters to multiple national records and helped athletes reach the world stage. He has also helped people return to sports after being told they may never compete again, and helped parents regain the strength and mobility to get down on the floor and play with their children.",
            "His coaching style is practical, individualized, and easy to understand. Rather than forcing everyone into the same system, Cam takes the time to understand each person’s history, goals, and current abilities before building a plan that fits their life. His approach has been shaped by years of hands-on coaching, mentorship, independent study, and continued learning through seminars and workshops.",
            "Whether someone wants to move without pain, lose weight, become stronger, or return to an activity they thought they had lost, Cam’s goal is the same: to help them build confidence in their body and become more capable in both sport and everyday life.",
        ],
    },
    {
        "key": "marina", "initials": "MM",
        "name": "Marina McCain",
        "role": "Registered Kinesiologist - Complex Rehab",
        "short": "Book with Marina",
        "bio": [
            "Marina is a Registered Kinesiologist with a certificate in Health and Fitness Studies. She has nearly 10 years of experience working with a wide range of clients, from people suffering from chronic pain to workplace injuries, to young athletes looking to improve their performance. Marina has a particular passion for helping clients work through injuries and get back to moving with confidence.",
            "Marina is an encouraging, detail-oriented, and direct coach who believes that change starts with being willing to try. She enjoys helping clients move the best they have ever moved and achieving their movement goals! As a lifelong competitive volleyball player and former competitive powerlifter and having suffered several injuries over the years, Marina brings first-hand experience with both athletic performance and injury recovery. Outside the gym, she enjoys watching and participating in motorsports, snowboarding, and playing video games.",
        ],
    },
]

STORIES = [
    ("JM", "Jonathan M.", [
        "“I was told it couldn't be fixed.”",
        "Inoperable nerve root compression. Drop foot.",
        "Couldn't stand, walk, or sit without pain.",
        "Tried physio, chiro, massage - nothing worked.",
        "Today? Skis. Runs. Jumps. Rows.",
        "Pain free for over a year.",
    ], "Same diagnosis. Different approach."),
    ("TW", "Tony W.", [
        "Lost 2/3 of his hand.",
        "Couldn't lift his arm halfway.",
        "L5-S1 disc extrusion.",
        "Most people would slow down.",
        "Tony broke 3 national bench press records at 63.",
        "Now in the best shape of his life.",
    ], "Not perfect structure - just the right system."),
    ("TD", "Trevor D.", [
        "Daily pain.",
        "Had to quit running, golf, and work on his farm.",
        "Multiple physio rounds → worse symptoms. Recommended surgery.",
        "Today? Back to work. Running. Golfing.",
        "Pain free. No surgery.",
    ], ""),
    ("BW", "Ben W.", [
        "Achilles + bursal tear.",
        "Couldn't run. Couldn't play with his kids.",
        "Tried injections. Tried physio. No progress.",
        "8 weeks later → back running.",
        "Now doing the Grouse Grind multiple times a week and returning to soccer.",
    ], ""),
    ("GB", "Gerry B.", [
        "Double knee replacement.",
        "Still in pain 1+ year later.",
        "Couldn't ski, bike, or play hockey. Had never squatted pain free in his life.",
        "Day 1: first pain-free squat.",
        "Weeks later → back to everything.",
    ], ""),
    ("JL", "Joe L.", [
        "Total knee replacement.",
        "Still in pain a year later.",
        "Hockey and golf didn't feel the same. Thought it was permanent.",
        "Now? Playing both multiple times a week pain free.",
        "Even recovered from a meniscus tear - no surgery needed.",
    ], ""),
]

NAV = [
    ("/pain/", "Pain"),
    ("/perform/", "Perform"),
    ("/young-forever/", "Young Forever"),
]
NAV_RIGHT = [
    ("/team/", "Meet the Team"),
    ("/contact/", "Contact Us"),
]

ARROW = ('<svg class="icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" '
         'focusable="false"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


# ---------------------------------------------------------------- layout
def jsonld_clinic():
    data = {
        "@context": "https://schema.org",
        "@type": "MedicalClinic",
        "name": NAME,
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/img/logo.png",
        "description": DESCRIPTION,
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ADDR_STREET,
            "addressLocality": ADDR_CITY,
            "addressRegion": ADDR_REGION,
            "postalCode": ADDR_POSTAL,
            "addressCountry": "CA",
        },
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False) + "</script>")


def header(current):
    def link(href, label):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{e(label)}</a>'

    left = "".join(link(h, l) for h, l in NAV)
    right = "".join(link(h, l) for h, l in NAV_RIGHT)
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="/" aria-label="{NAME} home"><img src="/img/logo.png" width="44" height="51" alt="" decoding="async"><span class="brand__name">{NAME}</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="nav-toggle__label">Menu</span><span class="nav-toggle__bars" aria-hidden="true"></span></button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <div class="site-nav__group">{left}</div>
      <span class="site-nav__divider" aria-hidden="true"></span>
      <div class="site-nav__group">{right}</div>
      <a class="btn btn--primary btn--sm site-nav__cta" href="/book/">Book Now</a>
    </nav>
  </div>
</header>"""


def footer():
    all_links = "".join(f'<li><a href="{h}">{e(l)}</a></li>' for h, l in
                        [("/", "Home")] + NAV + NAV_RIGHT + [("/book/", "Book Now")])
    return f"""<footer class="site-footer">
  <div class="container site-footer__grid">
    <div>
      <img class="site-footer__logo" src="/img/logo-white.png" width="60" height="70" alt="" loading="lazy" decoding="async">
      <p class="site-footer__name">{NAME}</p>
      <p class="site-footer__tag">{TAGLINE}</p>
    </div>
    <div>
      <h2 class="site-footer__h">Explore</h2>
      <ul class="site-footer__list">{all_links}</ul>
    </div>
    <div>
      <h2 class="site-footer__h">Visit &amp; contact</h2>
      <address class="site-footer__addr">
        <a href="{MAPS_URL}" rel="noopener">{e(ADDR_STREET)}<br>{ADDR_CITY} {ADDR_REGION} {ADDR_POSTAL}</a><br>
        <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
      </address>
    </div>
  </div>
  <div class="container site-footer__legal"><p>&copy; <span id="year">2026</span> {NAME}. All rights reserved.</p><p class="site-footer__links"><a href="/privacy/">Privacy Policy</a> <a href="/terms/">Terms of Use</a></p><p class="site-footer__credit">Built by <a href="https://stackwell.digital" target="_blank" rel="noopener">stackwell.digital</a></p></div>
</footer>"""


import re


def finalize(doc):
    """Prefix internal page links with PREFIX (empty at the site root)."""
    def fix(m):
        return f'{m.group(1)}="{PREFIX}/{m.group(2)}"'
    doc = re.sub(r'(href|action)="/(?!/)(?!(?:css|img|js|fonts)/)([^"]*)"', fix, doc)
    return doc


def page(path, title, desc, body, current="", schema=False, body_class="", hidden=False):
    """Render a full HTML page to site/<path>/index.html (or site/<path> if .html)."""
    full_title = f"{title} | {NAME}" if title else f"{NAME} - {TAGLINE}"
    canonical = SITE_URL + PREFIX + (path if path.endswith("/") else "/" + path.lstrip("/"))
    robots = '<meta name="robots" content="noindex, nofollow">\n' if (DEMO or hidden) else ""
    ld = jsonld_clinic() if schema else ""
    doc = f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<meta name="theme-color" content="#005745">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/img/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="/img/logo.png">
<link rel="apple-touch-icon" href="/img/logo.png">
<link rel="preload" href="/fonts/montserrat-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/open-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
{"".join(f'<link rel="stylesheet" href="{c}">\n' for c in CSS)}

{ld}
</head>
<body class="{body_class} {THEME}">
{header(current)}
<main id="main">
{body}
</main>
{footer()}
<script src="/js/config.js" defer></script>
<script src="/js/main.js" defer></script>
<script src="/js/analytics.js" defer></script>
</body>
</html>
"""
    doc = finalize(doc)
    base = OUT / PREFIX.strip("/")
    dest = base / path.strip("/") / "index.html" if path.endswith("/") else base / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc, encoding="utf-8")
    return canonical


# ---------------------------------------------------------------- components
def hero(eyebrow, h1, text, ctas, extra_class=""):
    return f"""<section class="hero {extra_class}">
  <div class="container hero__inner">
    {f'<p class="eyebrow eyebrow--light">{e(eyebrow)}</p>' if eyebrow else ''}
    <h1 class="hero__title">{h1}</h1>
    <p class="hero__text">{e(text)}</p>
    <div class="hero__actions">{ctas}</div>
  </div>
</section>"""


def book_btn(label="Book Now", cls="btn--primary", key="general"):
    return f'<a class="btn {cls}" href="/book/" data-jane="{key}">{e(label)}</a>'


def cta_band(heading, text, label="Book Now", key="general"):
    sub = f'<p>{e(text)}</p>' if text else ""
    return f"""<section class="cta-band">
  <div class="container cta-band__inner">
    <h2>{e(heading)}</h2>
    {sub}
    {book_btn(label, "btn--light", key)}
  </div>
</section>"""


def check_list(items):
    li = "".join(f"<li>{e(i)}</li>" for i in items)
    return f'<ul class="check-list">{li}</ul>'


# ---------------------------------------------------------------- pages
def build_home():
    body = hero(
        "Functional health · Performance · Pain resolution",
        "Find your<br>better",
        "A fully customized approach to health and performance that takes you from where you are to where you want to be, backed by an unparalleled promise.",
        '<a class="btn btn--light" href="#pathways">Choose Your Pathway ' + ARROW + '</a>'
        '<a class="btn btn--ghost" href="/book/" data-jane="general">Book Now</a>',
        "hero--home hero--tall",
    )
    body += f"""
<section class="section" id="pathways" aria-labelledby="pathways-h">
  <div class="container">
    <header class="section-head section-head--center">
      <p class="eyebrow">Three pathways, one promise</p>
      <h2 id="pathways-h">Where do you want to go?</h2>
      <p class="lede">Better Forever's approach is built around you. Whether you're sidelined with pain, just making the first step in your physical journey, or a high-level athlete at the top of your game - your ceiling is higher with Better Forever, and it's risk free.</p>
    </header>
    <div class="grid grid--3">
      <a class="card card--link" href="/pain/">
        <h3 class="card__title">I want to get out of pain</h3>
        <p>If pain is in the way of doing what you love, we find the real cause, and focus on the entire system - not just the painful area. Backed by our money-back promise - even if nothing else has worked.</p>
        <span class="card__more">Get out of pain {ARROW}</span>
      </a>
      <a class="card card--link" href="/young-forever/">
        <h3 class="card__title">I want to be young forever</h3>
        <p>Want to be the next one of our clients achieving the best shape of their lives in their 40s, 50s, 60s and beyond? Stay strong, sharp, and independent - for as long as you want to be.</p>
        <span class="card__more">Stay young forever {ARROW}</span>
      </a>
      <a class="card card--link" href="/perform/">
        <h3 class="card__title">I want to dominate the competition</h3>
        <p>World and national record-producing strength and conditioning. Used by Olympic, collegiate, and professional athletes to gain an unfair advantage. Are you next?</p>
        <span class="card__more">Perform at my best {ARROW}</span>
      </a>
    </div>
    <figure class="photo photo--banner photo--floor"><img src="/img/gym-floor.jpg" width="1280" height="960" alt="The Better Forever training floor, with squat racks, dumbbells and the painted logo wall" loading="lazy" decoding="async"></figure>
  </div>
</section>

<section class="section section--sage" aria-labelledby="why-h">
  <div class="container grid grid--2 grid--center">
    <div>
    <p class="eyebrow">Why we exist</p>
    <h2 id="why-h" class="statement">We believe no one should suffer life-limiting pain, and no one should accept &ldquo;good enough&rdquo; for their body.</h2>
    <p class="lede">Through an integrated, multimodal approach we move you from pain to function to performance - and keep you there.</p>
    <div class="btn-row">
      {book_btn("Book Now", "btn--primary")}
      <a class="btn btn--outline" href="/team/">Meet the team {ARROW}</a>
    </div>
  </div>
    <figure class="photo photo--tall"><img src="/img/physio-2.jpg" width="900" height="1348" alt="Hands-on manual therapy on the shoulder" loading="lazy" decoding="async"></figure>
  </div>
</section>
"""
    return page("/", "", DESCRIPTION, body, "/", schema=True)


def build_pain():
    stories = []
    for i, (ini, name, lines, tag) in enumerate(STORIES, 1):
        li = "".join(f"<p>{e(l)}</p>" for l in lines)
        tag_html = f'<p class="story__tag">{e(tag)}</p>' if tag else ""
        stories.append(f"""<article class="story" role="group" aria-roledescription="slide" aria-label="Story {i} of {len(STORIES)}: {e(name)}">
  <div class="story__avatar" aria-hidden="true">{ini}</div>
  <h3 class="story__name">{e(name)}</h3>
  <div class="story__body">{li}</div>
  {tag_html}
  <p class="story__count">{i:02d}/{len(STORIES):02d}</p>
</article>""")
    dots = "".join(
        f'<button type="button" class="carousel__dot" aria-label="Show story {i} of {len(STORIES)}: {e(n)}"></button>'
        for i, (_, n, _, _) in enumerate(STORIES, 1))

    body = hero(
        "If you're in pain",
        "Help me get out<br>of pain",
        "You're not broken. You just haven't had a system that understands your body, adapts in real time, and takes you all the way back to full function.",
        book_btn("Book Now", "btn--light") +
        '<a class="btn btn--ghost" href="#proof">See the proof ↓</a>',
        "hero--pain",
    )
    body += f"""
<section class="section section--tight" aria-label="Our risk free promise">
  <div class="container grid grid--3">
    <div class="stat-card"><h2 class="stat-card__h">1-Month Risk Free Improvement</h2><p>You get better or you get your money back. Simple as that.</p></div>
    <div class="stat-card"><h2 class="stat-card__h">First Session Risk Free</h2><p>Billed after you leave the building. You only pay if you found it valuable.</p></div>
    <div class="stat-card"><h2 class="stat-card__h">Over 90% Success Rate</h2><p>Including with cases that have failed elsewhere - multiple times.</p></div>
  </div>
</section>

<section class="section section--white" aria-labelledby="familiar-h">
  <div class="container grid grid--2 grid--split">
    <div>
      <p class="eyebrow">If this sounds familiar</p>
      <h2 id="familiar-h">You know this feeling</h2>
      {check_list([
        "Feeling hopeless, stuck, not sure where to turn next",
        "Felt like you've tried everything and you're not getting better",
        "Daily pain sits like a cloud over everyday life",
        "Can't play with your kids, having to say no to social events"])}
    </div>
    <div class="panel panel--green">
      <p class="eyebrow eyebrow--light">What's possible</p>
      <h2>Beyond baseline</h2>
      {check_list([
        "Live life on your own terms again",
        "Empowered to not just make it through the day - to thrive",
        "Beyond baseline. Not just better. Better than before.",
        "Able to show up for yourself and the people you care about"])}
    </div>
    <figure class="photo photo--banner"><img src="/img/physio-1.jpg" width="1200" height="801" alt="A therapist guiding a client through a hands-on leg mobilization" loading="lazy" decoding="async"></figure>
  </div>
</section>

<section class="section" id="proof" aria-labelledby="proof-h">
  <div class="container">
    <header class="section-head section-head--center">
      <p class="eyebrow">Real people. Real results.</p>
      <h2 id="proof-h">Same diagnosis. Different approach.</h2>
      <p class="lede">Six stories from people who were told it couldn't be fixed - or that this was as good as it gets.</p>
    </header>
    <div class="carousel" role="region" aria-roledescription="carousel" aria-label="Success stories">
      <div class="carousel__track">{''.join(stories)}</div>
      <div class="carousel__controls">
        <button type="button" class="carousel__btn carousel__prev" aria-label="Previous success story">&larr;</button>
        <div class="carousel__dots">{dots}</div>
        <button type="button" class="carousel__btn carousel__next" aria-label="Next success story">&rarr;</button>
      </div>
    </div>
    <div class="center-row">
      <p class="lede">Ready to write your own success story?</p>
      {book_btn("Book Now")}
    </div>
  </div>
</section>

<section class="section section--white" aria-labelledby="diff-h">
  <div class="container">
    <header class="section-head">
      <p class="eyebrow">A different approach for when nothing else has worked</p>
      <h2 id="diff-h">From Pain &rarr; Function &rarr; Performance</h2>
      <p class="lede">If you've been dealing with pain, you've probably tried:</p>
      {check_list(["Rest", "Rehab exercises", "Treatments that didn't work - or made things worse", "Treatments that helped… but didn't last"])}
      <p class="lede lede--strong">The problem isn't that nothing works.<br>It's that most approaches are incomplete.</p>
    </header>
    <h3 class="subhead">What makes this different</h3>
    <div class="grid grid--2">
      <div class="card"><h4 class="card__title">We don't just treat the pain</h4><p>Pain is rarely the real problem. We identify why your body is moving the way it is, what your brain is protecting, and what's actually causing the breakdown.</p></div>
      <div class="card"><h4 class="card__title">We fix the system - not just the injury</h4><p>Instead of chasing one area, we improve how your entire body works together. We build stability, control, and strength around weak points, and create a system that doesn't break down again.</p></div>
      <div class="card"><h4 class="card__title">We get results quickly - and prove it</h4><p>Every step follows Test &rarr; Fix &rarr; Retest. If something works, you'll feel it immediately. If it doesn't, we change the approach.</p></div>
      <div class="card"><h4 class="card__title">We build you back stronger than before</h4><p>Even if something doesn't fully heal, you can still move without pain, live life on your terms, and return to the activities you care about. Most people come back stronger and more capable than before injury.</p></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="why-works-h">
  <div class="container">
    <h2 id="why-works-h" class="center">Why this works when others haven't</h2>
    <div class="compare">
      <div class="compare__col compare__col--old">
        <h3>Most systems</h3>
        <ul><li>Focus only on the injured area</li><li>Stop once pain decreases</li><li>Don't prepare you for real-world demands</li></ul>
      </div>
      <div class="compare__col compare__col--new">
        <h3>This system</h3>
        <ul><li>Finds the real cause</li><li>Fixes how your body moves</li><li>Builds the resiliency to keep it that way</li></ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--sage" aria-labelledby="bottom-h">
  <div class="container prose-wide center">
    <p class="eyebrow">Bottom line</p>
    <h2 id="bottom-h" class="statement">You're not broken.</h2>
    <p class="lede">You just haven't had a system that understands your body, adapts in real time, and takes you all the way back to full function.</p>
    <p class="lede lede--strong">This one does. And it's risk free.</p>
    {book_btn("Book Now")}
  </div>
</section>
"""
    return page("/pain/", "Get Out of Pain in Langley, BC",
                "Pain stopping you from doing what you love? Better Forever in Langley, BC finds the real cause and fixes the whole system, with a risk free 1-month improvement offer.",
                body, "/pain/")


def build_perform():
    sports = ["Track and Field", "Volleyball", "Hockey", "NFL / CFL",
              "UFC / MMA / Jiu-Jitsu", "NLL", "Showjumping"]
    chips = "".join(f"<li>{e(s)}</li>" for s in sports)
    body = hero(
        "If you compete",
        "I want to dominate<br>the competition",
        "World and national record-producing strength and conditioning. Built for the athletes who'd rather earn the edge than wait for one.",
        book_btn("Book Now", "btn--light") +
        '<a class="btn btn--ghost" href="#athletes">See who we train ↓</a>',
        "hero--perform",
    )
    body += f"""
<section class="section" aria-labelledby="proof-h">
  <div class="container">
    <header class="section-head section-head--center">
      <p class="eyebrow">The proof is the record book</p>
      <h2 id="proof-h">What sets the program apart</h2>
    </header>
    <div class="grid grid--4">
      <div class="stat"><p class="stat__num">Multiple</p><h3 class="stat__label">World &amp; national records</h3><p>A strength and conditioning team with a track record of producing record-holding athletes.</p></div>
      <div class="stat"><p class="stat__num">8+</p><h3 class="stat__label">Pro &amp; Olympic sports</h3><p>Athletes from the NFL, CFL, NLL, UFC, track and field, volleyball, hockey, showjumping, and more.</p></div>
      <div class="stat"><p class="stat__num">10-15%</p><h3 class="stat__label">Average improvement</h3><p>What most athletes see in their first 12 weeks training with Better Forever.</p></div>
      <div class="stat"><p class="stat__num">1 Month</p><h3 class="stat__label">Risk free improvement</h3><p>We back our work with a measurable, risk free offer. If we don't deliver, you don't pay.</p></div>
    </div>
    <figure class="photo photo--banner photo--db"><img src="/img/gym-dumbbells.jpg" width="1000" height="1013" alt="Rows of heavy dumbbells on red racks in front of the Better Forever logo wall" loading="lazy" decoding="async"></figure>
  </div>
</section>

<section class="section section--white" id="athletes" aria-labelledby="athletes-h">
  <div class="container grid grid--2 grid--center">
    <figure class="photo photo--tall"><img src="/img/gym-rack.jpg" width="780" height="1040" alt="A power rack and loaded barbell on the Better Forever training floor" loading="lazy" decoding="async"></figure>
    <div>
    <header class="section-head">
      <p class="eyebrow">Athletes we train</p>
      <h2 id="athletes-h">Olympic. Collegiate. Professional.</h2>
      <p class="lede">We've worked with athletes across every level - from juniors chasing their first scholarship to pros chasing the next title.</p>
    </header>
    <ul class="chips">{chips}</ul>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="guar-h">
  <div class="container">
    <div class="panel panel--green panel--center">
      <h2 id="guar-h">Risk free performance</h2>
      <p class="lede">We back our work with a risk free 1-month improvement offer. Most athletes see a 10-15% improvement in their first 12 weeks with Better Forever - measurable, repeatable, and built to stack on top of itself.</p>
      {book_btn("Book a Performance Assessment", "btn--light")}
    </div>
  </div>
</section>

<section class="section section--white" aria-labelledby="out-h">
  <div class="container">
    <header class="section-head">
      <p class="eyebrow">What you walk away with</p>
      <h2 id="out-h">The outcomes our athletes chase - and hit</h2>
    </header>
    <div class="grid grid--2">
      <div class="card"><h3 class="card__title">Scholarships and professional careers</h3><p>Get noticed. Get drafted. Get paid to do what you love.</p></div>
      <div class="card"><h3 class="card__title">More playing time. Make the team.</h3><p>Earn your spot on the competitive roster - and keep it.</p></div>
      <div class="card"><h3 class="card__title">Break personal records and plateaus</h3><p>Move the numbers that have been stuck for years.</p></div>
      <div class="card"><h3 class="card__title">Improve resiliency and reduce injury risk</h3><p>Stay on the field. Train harder. Recover faster.</p></div>
      <div class="card card--wide"><h3 class="card__title">An unfair advantage over your competition</h3><p>The work nobody sees is what shows up on game day.</p></div>
    </div>
  </div>
</section>
"""
    body += cta_band("Find your unfair advantage.",
                     "Book a performance assessment and we'll show you exactly what's leaving points on the table - and how we close it.")
    return page("/perform/", "Athletic Performance Training in Langley, BC",
                "World and national record-producing strength and conditioning for Olympic, collegiate, and professional athletes in Langley, BC.",
                body, "/perform/")


def build_young():
    body = hero(
        "If you want it for life",
        "I want to be<br>young forever",
        "Many of our clients are in the best shape of their lives in their 40s, 50s, 60s and beyond - even with no prior training or athletic background.",
        book_btn("Book Now", "btn--light") +
        '<a class="btn btn--ghost" href="#possible">See what\'s possible ↓</a>',
        "hero--young",
    )
    body += f"""
<section class="section section--white">
  <div class="container prose-wide">
    <h2 class="statement">You're allowed to want more out of this decade.</h2>
    <p class="lede">Most people quietly accept the trade-offs of getting older. They stop trying things. They stop saying yes. They stop showing up the way they want to.</p>
    <p class="lede lede--strong">You don't have to.</p>
  </div>
</section>

<section class="section" id="possible" aria-labelledby="possible-h">
  <div class="container">
    <header class="section-head section-head--center"><h2 id="possible-h">What's possible</h2></header>
    <div class="grid grid--3">
      <div class="card"><h3 class="card__title">Do the things you love - for as long as you want to do them</h3>{check_list(["Skiing, golf, mountain biking, hockey", "Working in the yard, gardening", "Fishing, hiking, anything outdoors"])}</div>
      <div class="card"><h3 class="card__title">Say yes to adventures</h3>{check_list(["Enjoy vacations again", "Say yes to adventures", "Stop worrying if your body will hold up"])}</div>
      <div class="card"><h3 class="card__title">Stay sharp, confident, independent</h3>
        <dl class="def">
          <dt>Stay mentally sharp</dt><dd>Confident, focused, present</dd>
          <dt>Stay confident in your body</dt><dd>In how it moves. In how it looks.</dd>
          <dt>Stay independent</dt><dd>Not waiting on anyone. Not relying on anyone to get things done.</dd>
        </dl></div>
    </div>
  </div>
</section>

<section class="section section--white" aria-labelledby="fam-h">
  <div class="container grid grid--2 grid--split">
    <div>
      <p class="eyebrow">If this sounds familiar</p>
      <h2 id="fam-h">Does any of this sound like you?</h2>
      {check_list([
        "Is your body stiff and sore in ways it didn't used to be?",
        "Can't pick up your favourite activities without paying for it the next day?",
        "Is your body composition changing and you no longer like what you see in the mirror?",
        "Are you worried you'll become a burden to loved ones later in life?"])}
    </div>
    <div class="panel panel--green">
      <h2>It doesn't have to be this way.</h2>
      <p class="lede">Join our long list of success stories of people achieving the best shape of their lives in their 40s, 50s, 60s and beyond, even with no prior training experience. Experience a system that meets you where you are and takes you where you want to be.</p>
    </div>
  </div>
</section>
"""
    body += cta_band("Start saying yes to what life has to offer.",
                     "Book a starting conversation. We'll show you what the next chapter actually looks like.")
    return page("/young-forever/", "Strength, Longevity and Healthy Aging in Langley, BC",
                "Get in the best shape of your life in your 40s, 50s, 60s and beyond, with no prior training required. Better Forever, Langley, BC.",
                body, "/young-forever/")


def build_team():
    cards = []
    for m in TEAM:
        if m.get("photo"):
            avatar = (f'<div class="member__avatar member__avatar--photo"><span class="member__initials" aria-hidden="true">{m["initials"]}</span>'
                      f'<img src="{m["photo"]}" width="160" height="160" alt="{e(m["name"])}" loading="lazy" decoding="async" data-fallback></div>')
        else:
            avatar = f'<div class="member__avatar" aria-hidden="true"><span class="member__initials">{m["initials"]}</span></div>'
        paras = "".join(f"<p>{e(p)}</p>" for p in m["bio"])
        cards.append(f"""<article class="member" id="{m['key']}">
  {avatar}
  <div class="member__main">
    <h2 class="member__name">{e(m['name'])}</h2>
    <p class="member__role">{e(m['role'])}</p>
    <p class="member__lead">{e(m['bio'][0])}</p>
    <details class="member__more">
      <summary><span class="when-closed">Read more</span><span class="when-open">Show less</span></summary>
      <div class="member__bio">{''.join(f'<p>{e(p)}</p>' for p in m['bio'][1:])}</div>
    </details>
    <a class="btn btn--primary btn--sm" href="/book/" data-jane="{m['key']}">{e(m['short'])}</a>
  </div>
</article>""")
    body = hero(
        "Meet the team",
        "The people behind<br>Better Forever",
        "Decades of combined experience treating world-class athletes and everyday people who were told they had to live with it. They didn't. Neither do you.",
        book_btn("Book a Session", "btn--light"),
        "hero--short",
    )
    body += f"""
<section class="section">
  <div class="container team-list">{''.join(cards)}</div>
</section>
"""
    body += cta_band("Not sure who to start with?",
                     "That's exactly what our Book Now flow is for. We'll meet you where you are.",
                     "Start Your Journey")
    return page("/team/", "Meet the Team",
                "Naturopathic doctors, a chiropractor, a registered kinesiologist and record-producing strength coaches working as one team in Langley, BC.",
                body, "/team/")


def inquiry_form(form_id, intro_pathway=False):
    pathway = ""
    if intro_pathway:
        pathway = """
      <div class="field">
        <label for="f-path">What brings you in?</label>
        <select id="f-path" name="pathway">
          <option value="">Not sure yet</option>
          <option>I want to get out of pain</option>
          <option>I want to be young forever</option>
          <option>I want to dominate the competition</option>
        </select>
      </div>"""
    return f"""<form class="form" id="{form_id}" data-inquiry novalidate>
      <div class="field"><label for="{form_id}-name">Name</label><input id="{form_id}-name" name="name" type="text" autocomplete="name" required></div>
      <div class="field"><label for="{form_id}-email">Email</label><input id="{form_id}-email" name="email" type="email" autocomplete="email" required></div>
      {pathway}
      <div class="field"><label for="{form_id}-msg">Message</label><textarea id="{form_id}-msg" name="message" rows="5" required></textarea></div>
      <p class="form__note">Please do not include medical details in this form. See our <a href="/privacy/">Privacy Policy</a>.</p>
      <p class="form__status" role="status" aria-live="polite"></p>
      <button class="btn btn--primary" type="submit">Send Message</button>
    </form>"""


def build_contact():
    body = hero("Contact us", "We'd love to<br>hear from you",
                "Visit the center, give us a call, or send a quick note. For booking, head to the Book Now page - this form is for general inquiries.",
                book_btn("Book Now", "btn--light"), "hero--short")
    body += f"""
<section class="section">
  <div class="container grid grid--2 grid--split">
    <div class="contact-cards">
      <div class="info-card"><h2>Visit us</h2><p><a href="{MAPS_URL}" rel="noopener">{e(ADDR_STREET)}, {ADDR_CITY} {ADDR_REGION} {ADDR_POSTAL}</a></p></div>
      <div class="info-card"><h2>Call us</h2><p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div>
      <div class="info-card"><h2>Email us</h2><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
      <figure class="photo photo--wide"><img src="/img/gym-logo-rack.jpg" width="1000" height="833" alt="Dumbbell racks beneath the Better Forever logo at the center" loading="lazy" decoding="async"></figure>
    </div>
    <div class="panel">
      <h2>General inquiry</h2>
      <p>Have a question that isn't about booking? Drop us a note here and we'll route it to the right person.</p>
      {inquiry_form("contact-form")}
    </div>
  </div>
</section>
"""
    return page("/contact/", "Contact Us",
                f"Visit Better Forever at {ADDR_STREET}, {ADDR_CITY} {ADDR_REGION}, call {PHONE_DISPLAY}, or send a quick note.",
                body, "/contact/", schema=True)


def build_book():
    people = "".join(f"""<li class="pick"><div class="pick__info"><h3>{e(m['name'])}</h3><p>{e(m['role'])}</p></div>
        <a class="btn btn--primary btn--sm" href="#start" data-jane="{m['key']}">{e(m['short'])}</a></li>""" for m in TEAM)
    body = hero("Book now", "Let's find your<br>starting point",
                "Two ways in. Pick the one that fits where you are right now.", "", "hero--short")
    body += f"""
<section class="section" aria-labelledby="two-h">
  <div class="container">
    <h2 id="two-h" class="sr-only">Booking options</h2>
    <div class="grid grid--2 grid--split">
      <div class="panel" id="practitioners">
        <p class="eyebrow">Option 1</p>
        <h2>I know who I want to see</h2>
        <p>Pick a practitioner and go straight to their booking page.</p>
        <ul class="picks">{people}</ul>
      </div>
      <div class="panel panel--green" id="start">
        <p class="eyebrow eyebrow--light">Option 2</p>
        <h2>I'm just starting my journey</h2>
        <p>Tell us about you. We'll route you to the right person and get back as soon as we can.</p>
        <div class="form-on-dark">{inquiry_form("book-form", intro_pathway=True)}</div>
      </div>
    </div>
  </div>
</section>
"""
    return page("/book/", "Book Now",
                "Book with a Better Forever practitioner in Langley, BC, or tell us about yourself and we'll route you to the right person.",
                body, "/book/")


def build_joel():
    """Hidden review page for Joel. Not in nav, footer, sitemap or robots allow list. Always noindex."""
    m = next(t for t in TEAM if t["key"] == "joel")
    body = hero(
        "Head Trainer",
        "Train with<br>Joel McCain",
        "Fifteen years coaching strength athletes, and the creator of the CORE4 system. Schedule your sessions with Joel directly.",
        book_btn("Schedule with Joel", "btn--light", "joel") +
        '<a class="btn btn--ghost" href="#about">About Joel &darr;</a>',
        "hero--short",
    )
    body += f"""
<section class="section section--tight" aria-label="Draft notice">
  <div class="container">
    <div class="draft-note">
      <p class="eyebrow">Draft for Joel</p>
      <p>This page is not public and not linked anywhere on the site. It is here so you can tell us what to keep, cut and change. Questions are at the bottom.</p>
    </div>
  </div>
</section>

<section class="section" id="about" aria-labelledby="about-h">
  <div class="container joel-intro">
    <div class="joel-intro__photo">
      <span class="member__initials" aria-hidden="true">{m['initials']}</span>
      <img src="{m['photo']}" width="480" height="560" alt="{e(m['name'])}" loading="lazy" decoding="async" data-fallback>
    </div>
    <div>
      <header class="section-head">
        <p class="eyebrow">About Joel</p>
        <h2 id="about-h">Strength coach. Record holder. Builder of CORE4.</h2>
      </header>
      {"".join(f"<p>{e(p)}</p>" for p in m['bio'])}
    </div>
  </div>
</section>

<section class="section section--white" aria-labelledby="core4-h">
  <div class="container">
    <header class="section-head">
      <p class="eyebrow">The system</p>
      <h2 id="core4-h">CORE4 and CORE4+</h2>
      <p class="lede">Joel built CORE4 with the Better Forever team after his own long road through the medical system. It is made for people dealing with injuries and chronic pain who want to move without it.</p>
    </header>
    <div class="grid grid--2">
      <div class="card"><h3 class="card__title">CORE4</h3><p>Placeholder. Joel, tell us in your own words what CORE4 is and who it is for.</p></div>
      <div class="card"><h3 class="card__title">CORE4+</h3><p>Placeholder. What is different about CORE4+, and who moves up to it.</p></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="who-h">
  <div class="container">
    <header class="section-head">
      <p class="eyebrow">Who Joel coaches</p>
      <h2 id="who-h">From first sessions to record attempts</h2>
    </header>
    {check_list([
        "Four world record holding strength athletes",
        "National and provincial record holders",
        "Collegiate, professional and Olympic athletes across more than 15 sports",
        "People with injuries and chronic pain who were told to live with it",
    ])}
  </div>
</section>

<section class="section section--white" aria-labelledby="sched-h">
  <div class="container">
    <div class="panel panel--green panel--center">
      <h2 id="sched-h">Schedule with Joel</h2>
      <p class="lede">Pick a time that works. This booking page is schedule only, so there is nothing to fill out first.</p>
      {book_btn("Schedule with Joel", "btn--light", "joel")}
    </div>
  </div>
</section>

<section class="section" aria-labelledby="qs-h">
  <div class="container">
    <header class="section-head">
      <p class="eyebrow">For Joel</p>
      <h2 id="qs-h">Tell us what you want this to be</h2>
    </header>
    <div class="grid grid--2">
      <div class="card"><h3 class="card__title">Look and feel</h3><p>Keep it matched to the center, or give your own work a different feel? Send any pages or sites you like.</p></div>
      <div class="card"><h3 class="card__title">Photos</h3><p>We need a clear portrait of you and one or two shots of you coaching. Real photos only.</p></div>
      <div class="card"><h3 class="card__title">What to say</h3><p>Which of the sections above stay, which go, and what is missing. CORE4 and CORE4+ copy needs to come from you.</p></div>
      <div class="card"><h3 class="card__title">Booking</h3><p>Your outside clients move into the center system by Nov 1. Tell us which session types should be bookable from this page.</p></div>
    </div>
    <div class="btn-row">
      <a class="btn btn--primary" href="mailto:{EMAIL}?subject=Joel%20page%20feedback">Send feedback</a>
    </div>
  </div>
</section>
"""
    return page("/joel/", "Train with Joel McCain",
                "Schedule with Joel McCain, head trainer and creator of CORE4 at Better Forever in Langley, BC.",
                body, "", hidden=True)


def todo(text):
    return f'<mark class="todo">[{e(text)}]</mark>'


def legal_page(path, title, desc, intro, sections):
    body = hero("Legal", title.replace(" ", "<br>", 1), desc, "", "hero--short")
    secs = "".join(f"<h2>{e(h)}</h2>{b}" for h, b in sections)
    body += f"""
<section class="section" aria-label="{e(title)}">
  <div class="container legal">
    <p class="legal__date">Effective date: November 1, 2026. Last updated: October 28, 2026.</p>
    {intro}
    {secs}
  </div>
</section>
"""
    return page(path, title, desc, body, "")


def build_privacy():
    S = []
    S.append(("Who we are", f"""<p>{NAME} operates this website and the center at {e(ADDR_STREET)}, {ADDR_CITY} {ADDR_REGION} {ADDR_POSTAL}. This policy explains what personal information this website collects, why, and what your choices are.</p>
<p>Privacy contact: Eilah B. Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>"""))
    S.append(("What we collect on this website", """<ul>
<li><strong>Contact form.</strong> Your name, email address, the message you write, and your optional choice of what brings you in.</li>
<li><strong>Website analytics.</strong> On betterforever.ca we use Google Analytics 4. It records pages viewed, device and browser type, approximate location (city level), how you arrived, and whether you tap the booking, phone or email links. It uses cookies.</li>
<li><strong>Technical data.</strong> Our hosting provider, Cloudflare, processes your IP address and request details to deliver and protect the site.</li>
<li><strong>Online booking.</strong> The Book Now buttons take you to Jane App, our booking and patient records software. What you enter there is handled under the center's practices and Jane's own privacy policy, not this website.</li>
</ul>"""))
    S.append(("Health information", """<p>Please do not send medical details, symptoms or diagnoses through the contact form or by regular email. For anything about your care, call us or book an appointment.</p>"""))
    S.append(("How we use it", """<ul>
<li>To reply to your message.</li>
<li>To understand how the site is used and to improve it.</li>
<li>To keep the site secure.</li>
</ul>
<p>We do not sell your personal information and we do not use it for advertising.</p>"""))
    S.append(("Who handles it for us", """<ul>
<li><strong>Resend</strong> delivers contact form messages to our inbox. Its servers are in the United States.</li>
<li><strong>Google</strong> provides website analytics. Data is processed in the United States and other countries.</li>
<li><strong>Cloudflare</strong> hosts and protects this website.</li>
<li><strong>Jane App</strong> provides online booking, as described above.</li>
</ul>
<p>Because of this, your information may be stored or processed outside Canada, where privacy laws may differ and authorities may be able to access it.</p>"""))
    S.append(("Your consent and choices", """<p>By sending the contact form you agree that we may use what you submit to respond to you. You can withdraw your consent at any time by contacting us, subject to legal or contractual limits.</p>
<p>You can block or delete cookies in your browser settings, or install Google's analytics opt out browser add on, and the site will still work.</p>"""))
    S.append(("How long we keep it", f"""<p>Contact form messages are kept for 6 months and then deleted. Website analytics event data is kept for 2 months and user data for 14 months.</p>"""))
    S.append(("Access, correction and complaints", f"""<p>You can ask to see the personal information we hold about you, or ask us to correct it, by contacting our privacy contact above. We will respond within the time required by law.</p>
<p>If you are not satisfied with our response, you can contact the Office of the Information and Privacy Commissioner for British Columbia at <a href="https://www.oipc.bc.ca" rel="noopener">oipc.bc.ca</a>.</p>"""))
    S.append(("Changes to this policy", """<p>We may update this policy from time to time. The date at the top shows when it was last changed.</p>"""))
    return legal_page("/privacy/", "Privacy Policy",
                      "How Better Forever collects, uses and protects personal information on this website.",
                      "", S)


def build_terms():
    S = []
    S.append(("About this website", """<p>The information on this website is general and for education only. It is not medical advice, and it does not diagnose or treat any condition. Reading the site or sending a message does not create a patient relationship with the center or any of its practitioners.</p>
<p>If you think you have a medical emergency, call 911.</p>"""))
    S.append(("Booking and appointments", f"""<p>Appointments are booked through Jane App and are subject to the center's policies, including a 24 hour cancellation policy. Jane App has its own terms and privacy policy.</p>"""))
    S.append(("The Better Forever plan and the Risk Free offer", f"""<p>The Risk Free offer applies to the Better Forever plan only. It does not apply to ancillary services such as RMT, chiropractic and kinesiology, which support the training programs.</p>
<p>Improvement is measured through a personal training program, using the baseline of the Core 4 assessment.</p>
<p>Stories and descriptions on this site are not a promise of any particular result. Results differ from person to person.</p>"""))
    S.append(("Our content", """<p>The text, photos, logos and design on this website belong to Better Forever or its licensors. You may view and share pages for personal, non commercial use. Please ask us before reusing anything else.</p>"""))
    S.append(("Links to other sites", """<p>This website links to services we do not control, such as Jane App and Google Maps. We are not responsible for their content or practices.</p>"""))
    S.append(("Limits of liability", """<p>This website is provided as is. To the extent the law allows, Better Forever is not responsible for losses that result from using this website or relying on its content. This does not limit any responsibility a practitioner has for the services they provide.</p>"""))
    S.append(("Governing law", """<p>These terms are governed by the laws of British Columbia and the federal laws of Canada that apply there. Any dispute will be handled by the courts of British Columbia.</p>"""))
    S.append(("Changes and contact", f"""<p>We may update these terms from time to time. Questions? Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>"""))
    return legal_page("/terms/", "Terms of Use",
                      "The terms for using the Better Forever website, booking, and the Risk Free offer.",
                      "", S)


def build_all(prefix, css, theme):
    global PREFIX, CSS, THEME
    PREFIX, CSS, THEME = prefix, css, theme
    urls = [build_home(), build_pain(), build_perform(), build_young(),
            build_team(), build_contact(), build_book(),
            build_privacy(), build_terms()]
    build_joel()  # hidden: deliberately not in the returned list, so never in the sitemap
    return urls
