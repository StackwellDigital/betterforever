// GET / PUT / DELETE /api/admin/posts/<id>
import { jsonResponse, cleanInput } from "../../../_lib/blog.js";

const idOf = (p) => (/^\d{1,10}$/.test(String(p.id)) ? Number(p.id) : null);

export async function onRequestGet({ env, params }) {
  const id = idOf(params);
  if (!id) return jsonResponse({ error: "Not found." }, 404);
  const post = await env.DB.prepare("SELECT * FROM posts WHERE id = ?").bind(id).first();
  return post ? jsonResponse({ post }) : jsonResponse({ error: "Not found." }, 404);
}

export async function onRequestPut({ request, env, params, data }) {
  const id = idOf(params);
  if (!id) return jsonResponse({ error: "Not found." }, 404);
  let raw;
  try { raw = await request.json(); } catch { return jsonResponse({ error: "Bad request." }, 400); }
  const version = Number(raw && raw.version);
  if (!Number.isInteger(version) || version < 1) return jsonResponse({ error: "Bad request." }, 400);

  const existing = await env.DB.prepare("SELECT * FROM posts WHERE id = ?").bind(id).first();
  if (!existing) return jsonResponse({ error: "Not found." }, 404);
  const c = cleanInput(raw, existing);
  if (c.error) return jsonResponse({ error: c.error }, 400);
  const v = c.value;
  try {
    const r = await env.DB.prepare(
      `UPDATE posts SET slug = ?, title = ?, excerpt = ?, body_md = ?, cover_url = ?, cover_alt = ?, author = ?,
         status = ?, published_at = ?, version = version + 1, updated_by = ?,
         updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
       WHERE id = ? AND version = ?`
    ).bind(v.slug, v.title, v.excerpt, v.body_md, v.cover_url, v.cover_alt, v.author, v.status, v.published_at, data.email, id, version).run();
    if (!r.meta.changes) {
      return jsonResponse({ error: `Someone else saved this post first${existing.updated_by ? " (" + existing.updated_by + ")" : ""}. Reload the page to get their changes.` }, 409);
    }
  } catch (err) {
    if (/UNIQUE/i.test(err.message || "")) return jsonResponse({ error: "Another post already uses that web address." }, 409);
    throw err;
  }
  const post = await env.DB.prepare("SELECT * FROM posts WHERE id = ?").bind(id).first();
  return jsonResponse({ post });
}

export async function onRequestDelete({ env, params }) {
  const id = idOf(params);
  if (!id) return jsonResponse({ error: "Not found." }, 404);
  await env.DB.prepare("DELETE FROM posts WHERE id = ?").bind(id).run();
  return jsonResponse({ ok: true });
}
