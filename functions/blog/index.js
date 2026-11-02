// GET /blog/ : list of published posts, newest first.
import { htmlResponse, layout, cardHtml, todayVancouver, PAGE_SIZE, notFoundPage, unavailablePage } from "../_lib/blog.js";
import { CTA_BAND } from "../_lib/shell.js";

const HERO = `<section class="hero hero--short">
  <div class="container hero__inner">
    <p class="eyebrow eyebrow--light">Blog</p>
    <h1 class="hero__title">Better Forever<br>Blog</h1>
    <p class="hero__text">News and advice from the Better Forever team.</p>
    <div class="hero__actions"></div>
  </div>
</section>`;

export async function onRequestGet({ request, env }) {
  try {
    const url = new URL(request.url);
    const page = Math.max(1, Math.min(500, parseInt(url.searchParams.get("page") || "1", 10) || 1));
    const today = todayVancouver();
    const where = "status = 'published' AND published_at <= ?";
    const { n } = await env.DB.prepare(`SELECT COUNT(*) AS n FROM posts WHERE ${where}`).bind(today).first();
    const { results } = await env.DB.prepare(
      `SELECT slug, title, excerpt, substr(body_md, 1, 800) AS body_md, cover_url, cover_alt, published_at
       FROM posts WHERE ${where} ORDER BY published_at DESC, id DESC LIMIT ? OFFSET ?`
    ).bind(today, PAGE_SIZE, (page - 1) * PAGE_SIZE).all();
    if (page > 1 && !results.length) return notFoundPage(request);

    const pages = Math.max(1, Math.ceil(n / PAGE_SIZE));
    const link = (p) => (p === 1 ? "/blog/" : `/blog/?page=${p}`);
    const pager = pages > 1
      ? `<nav class="pager" aria-label="Pages of posts">${page > 1 ? `<a class="btn btn--outline btn--sm" href="${link(page - 1)}">Newer posts</a>` : ""}<span class="pager__now">Page ${page} of ${pages}</span>${page < pages ? `<a class="btn btn--outline btn--sm" href="${link(page + 1)}">Older posts</a>` : ""}</nav>`
      : "";
    const list = results.length
      ? `<ul class="post-grid">${results.map(cardHtml).join("\n")}</ul>${pager}`
      : `<p class="lede">No posts yet. Check back soon.</p>`;
    const body = `${HERO}
<section class="section" aria-label="Blog posts">
  <div class="container">
${list}
  </div>
</section>
${CTA_BAND}`;
    return htmlResponse(request, layout({
      title: page > 1 ? `Blog, page ${page}` : "Blog",
      description: "News and advice from the Better Forever team in Langley, BC.",
      path: link(page),
      body,
    }), { noindex: n === 0 });
  } catch (err) {
    console.error("blog index", err && err.message);
    return unavailablePage(request);
  }
}
export const onRequestHead = onRequestGet;
