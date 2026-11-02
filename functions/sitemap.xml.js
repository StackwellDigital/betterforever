// GET /sitemap.xml : the static page list (generated into shell.js) plus every published blog post.
import { SITE_URL, STATIC_PATHS } from "./_lib/shell.js";
import { todayVancouver } from "./_lib/blog.js";

const x = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;" }[c]));

export async function onRequestGet({ env }) {
  const urls = STATIC_PATHS.map((p) => `<url><loc>${x(SITE_URL + p)}</loc></url>`);
  try {
    const { results } = await env.DB.prepare(
      "SELECT slug, updated_at FROM posts WHERE status = 'published' AND published_at <= ? ORDER BY published_at DESC"
    ).bind(todayVancouver()).all();
    for (const r of results) urls.push(`<url><loc>${x(`${SITE_URL}/blog/${r.slug}/`)}</loc><lastmod>${x(String(r.updated_at).slice(0, 10))}</lastmod></url>`);
  } catch (err) {
    console.error("sitemap", err && err.message); // still serve the static pages
  }
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.join("")}</urlset>\n`,
    { headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=300" } });
}
