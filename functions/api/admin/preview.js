// POST /api/admin/preview : render a draft exactly as the public page will, without saving.
import { jsonResponse, articleHtml, MEDIA_URL, todayVancouver } from "../../_lib/blog.js";

export async function onRequestPost({ request }) {
  let r;
  try { r = await request.json(); } catch { return jsonResponse({ error: "Bad request." }, 400); }
  const cover = String(r.cover_url || "");
  const html = articleHtml({
    title: String(r.title || "Untitled").slice(0, 140),
    body_md: String(r.body_md || "").slice(0, 100000),
    cover_url: MEDIA_URL.test(cover) ? cover : "",
    cover_alt: String(r.cover_alt || "").slice(0, 200),
    author: String(r.author || "").slice(0, 100),
    published_at: /^\d{4}-\d{2}-\d{2}$/.test(String(r.published_at || "")) ? r.published_at : todayVancouver(),
  });
  return jsonResponse({ html });
}
