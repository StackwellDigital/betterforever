// GET /blog/<slug>/ : one published post. Drafts and scheduled posts return 404.
import { htmlResponse, layout, articleHtml, postLd, describe, todayVancouver, notFoundPage, unavailablePage } from "../_lib/blog.js";
import { CTA_BAND, SITE_URL } from "../_lib/shell.js";

export async function onRequestGet({ request, env, params }) {
  const slug = String(params.slug || "");
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug) || slug.length > 80) return notFoundPage(request);
  try {
    const post = await env.DB.prepare(
      `SELECT slug, title, excerpt, body_md, cover_url, cover_alt, author, published_at, updated_at
       FROM posts WHERE slug = ? AND status = 'published' AND published_at <= ?`
    ).bind(slug, todayVancouver()).first();
    if (!post) return notFoundPage(request);
    const body = `${articleHtml(post)}\n${CTA_BAND}`;
    return htmlResponse(request, layout({
      title: post.title,
      description: describe(post),
      path: `/blog/${post.slug}/`,
      body,
      ogType: "article",
      ogImage: post.cover_url ? SITE_URL + post.cover_url : "",
      ld: postLd(post),
    }));
  } catch (err) {
    console.error("blog post", err && err.message);
    return unavailablePage(request);
  }
}
export const onRequestHead = onRequestGet;
