// GET /api/admin/posts : all posts, drafts first.   POST /api/admin/posts : create.
import { jsonResponse, cleanInput, todayVancouver } from "../../../_lib/blog.js";

export async function onRequestGet({ env }) {
  const { results } = await env.DB.prepare(
    `SELECT id, slug, title, status, published_at, updated_at, updated_by
     FROM posts ORDER BY CASE WHEN status = 'draft' THEN 0 ELSE 1 END, published_at DESC, updated_at DESC LIMIT 500`
  ).all();
  return jsonResponse({ posts: results, today: todayVancouver() });
}

export async function onRequestPost({ request, env, data }) {
  let raw;
  try { raw = await request.json(); } catch { return jsonResponse({ error: "Bad request." }, 400); }
  const c = cleanInput(raw);
  if (c.error) return jsonResponse({ error: c.error }, 400);
  const v = c.value;
  try {
    const r = await env.DB.prepare(
      `INSERT INTO posts (slug, title, excerpt, body_md, cover_url, cover_alt, author, status, published_at, updated_by)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(v.slug, v.title, v.excerpt, v.body_md, v.cover_url, v.cover_alt, v.author, v.status, v.published_at, data.email).run();
    const post = await env.DB.prepare("SELECT * FROM posts WHERE id = ?").bind(r.meta.last_row_id).first();
    return jsonResponse({ post }, 201);
  } catch (err) {
    if (/UNIQUE/i.test(err.message || "")) return jsonResponse({ error: "Another post already uses that web address." }, 409);
    throw err;
  }
}
