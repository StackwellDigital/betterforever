// Shared helpers for the blog Functions: page layout (uses the generated site shell), validation, rendering.
import { SITE_URL, SITE_NAME, TEMPLATE, SECURITY_HEADERS } from "./shell.js";
import { renderMarkdown, markdownToText, imgTag, esc } from "./markdown.js";

export { esc };
export const PAGE_SIZE = 12;
export const MEDIA_URL = /^\/img\/blog\/[A-Za-z0-9/_.-]+$/;

export const todayVancouver = () => new Date().toLocaleDateString("en-CA", { timeZone: "America/Vancouver" });

export function formatDate(iso) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) return "";
  return new Date(iso + "T12:00:00Z").toLocaleDateString("en-CA", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
}

export function slugify(t) {
  return String(t || "")
    .normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .toLowerCase().replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80).replace(/-+$/g, "");
}

export function describe(post) {
  const t = (post.excerpt || "").trim() || markdownToText(post.body_md);
  return t.length > 160 ? t.slice(0, 157).replace(/\s+\S*$/, "") + "..." : t;
}

// ---- responses -------------------------------------------------------------------------------------------
const baseHeaders = (request, extra = {}) => {
  const h = new Headers({ ...SECURITY_HEADERS, ...extra });
  if (new URL(request.url).hostname.endsWith(".pages.dev")) h.set("X-Robots-Tag", "noindex"); // _headers does not apply to Functions
  return h;
};

export function htmlResponse(request, html, { status = 200, cache = "public, max-age=60", noindex = false } = {}) {
  const h = baseHeaders(request, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": status === 200 ? cache : "no-store" });
  if (noindex) h.set("X-Robots-Tag", "noindex");
  return new Response(html, { status, headers: h });
}

export function jsonResponse(data, status = 200, request) {
  const h = new Headers({
    "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff", "X-Robots-Tag": "noindex",
  });
  return new Response(JSON.stringify(data), { status, headers: h });
}

// ---- page layout -----------------------------------------------------------------------------------------
const safeJson = (o) => JSON.stringify(o).replace(/</g, "\\u003c");

export function layout({ title, description, path, body, ogType = "website", ogImage = "", ld = null }) {
  const map = {
    TITLE: esc(title),
    DESC: esc(description),
    CANONICAL: esc(SITE_URL + path),
    OGTYPE: esc(ogType),
    OGIMAGE: esc(ogImage || SITE_URL + "/img/logo.png"),
    LD: ld ? `<script type="application/ld+json">${safeJson(ld)}</script>` : "",
    BODY: body,
  };
  return TEMPLATE.replace(/\{\{([A-Z]+)\}\}/g, (_, k) => map[k] ?? "");
}

// ---- post rendering --------------------------------------------------------------------------------------
export function articleHtml(post) {
  const date = formatDate(post.published_at);
  const meta = [
    date ? `<time datetime="${esc(post.published_at)}">${esc(date)}</time>` : "",
    post.author ? `By ${esc(post.author)}` : "",
  ].filter(Boolean).join(" &middot; ");
  const cover = post.cover_url && MEDIA_URL.test(post.cover_url)
    ? `<figure class="container post__cover">${imgTag(post.cover_url, post.cover_alt || "", "").replace(' loading="lazy"', "")}</figure>`
    : "";
  return `<article class="post">
  <header class="post__head">
    <div class="container post__wrap">
      <p class="eyebrow"><a href="/blog/">Blog</a></p>
      <h1 class="post__title">${esc(post.title)}</h1>
      ${meta ? `<p class="post__meta">${meta}</p>` : ""}
    </div>
  </header>
  ${cover}
  <div class="container post__wrap">
    <div class="post__body">
${renderMarkdown(post.body_md)}
    </div>
    <p class="post__back"><a href="/blog/">&larr; All posts</a></p>
  </div>
</article>`;
}

export function postLd(post) {
  const url = `${SITE_URL}/blog/${post.slug}/`;
  const ld = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: describe(post),
    datePublished: post.published_at,
    dateModified: (post.updated_at || post.published_at || "").slice(0, 10),
    mainEntityOfPage: url,
    author: post.author ? { "@type": "Person", name: post.author } : { "@type": "Organization", name: SITE_NAME },
    publisher: { "@type": "Organization", name: SITE_NAME, logo: { "@type": "ImageObject", url: SITE_URL + "/img/logo.png" } },
  };
  if (post.cover_url) ld.image = SITE_URL + post.cover_url;
  return ld;
}

export function cardHtml(p) {
  const img = p.cover_url && MEDIA_URL.test(p.cover_url) ? imgTag(p.cover_url, p.cover_alt || "", ' class="post-card__img"') : "";
  const date = formatDate(p.published_at);
  return `<li><a class="card card--link post-card" href="/blog/${esc(p.slug)}/">
${img}<time class="post-card__date" datetime="${esc(p.published_at)}">${esc(date)}</time>
<h2 class="card__title">${esc(p.title)}</h2>
<p>${esc(describe(p))}</p>
<span class="card__more">Read more</span></a></li>`;
}

// ---- input validation (admin API) ------------------------------------------------------------------------
const validDate = (d) => /^\d{4}-\d{2}-\d{2}$/.test(d) && new Date(d + "T00:00:00Z").toISOString().slice(0, 10) === d;

export function cleanInput(raw, existing = null) {
  const r = raw && typeof raw === "object" ? raw : {};
  const str = (v, max) => String(v ?? "").replace(/\r\n?/g, "\n").trim().slice(0, max);
  const title = str(r.title, 140).replace(/\n/g, " ");
  if (!title) return { error: "Add a title." };

  const status = r.status === "published" ? "published" : "draft";
  let slug = slugify(r.slug || (existing ? existing.slug : title));
  if (existing && existing.status === "published" && existing.slug !== slug)
    return { error: "This post is live, so its web address can't change. Unpublish it first, or keep the address." };
  if (!slug) return { error: "Add a web address." };

  let published_at = String(r.published_at || "").trim();
  if (published_at && !validDate(published_at)) return { error: "That date doesn't look right." };
  if (status === "published" && !published_at) published_at = todayVancouver();

  const cover_url = String(r.cover_url || "").trim();
  if (cover_url && !MEDIA_URL.test(cover_url)) return { error: "Cover image must be uploaded through this page." };

  const body_md = String(r.body_md ?? "").replace(/\r\n?/g, "\n").slice(0, 100000);
  if (status === "published" && !body_md.trim()) return { error: "Write something before publishing." };

  return {
    value: {
      slug, title, status, published_at, cover_url,
      excerpt: str(r.excerpt, 300).replace(/\n/g, " "),
      cover_alt: str(r.cover_alt, 200).replace(/\n/g, " "),
      author: str(r.author, 100).replace(/\n/g, " "),
      body_md,
    },
  };
}

// ---- shared error pages ----------------------------------------------------------------------------------
export function notFoundPage(request) {
  const body = `<section class="section"><div class="container post__wrap"><h1>That page doesn't exist.</h1><p><a href="/blog/">Back to the blog</a></p></div></section>`;
  return htmlResponse(request, layout({ title: "Page not found", description: "This page doesn't exist.", path: "/blog/", body }), { status: 404 });
}

export function unavailablePage(request) {
  const body = `<section class="section"><div class="container post__wrap"><h1>The blog is taking a short break.</h1><p>Please try again in a few minutes, or <a href="/contact/">contact us</a>.</p></div></section>`;
  return htmlResponse(request, layout({ title: "Blog unavailable", description: "The blog is temporarily unavailable.", path: "/blog/", body }), { status: 503 });
}
