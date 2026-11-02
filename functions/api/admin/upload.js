// POST /api/admin/upload : one image per request (multipart field "file"), stored in R2.
// The editor already resized and re-encoded it to JPEG in the browser (which also drops EXIF).
// The server still checks size and the file's real type, so it never trusts the browser.
import { jsonResponse } from "../../_lib/blog.js";

const MAX = 8 * 1024 * 1024;

function sniff(b) {
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return { ext: "jpg", type: "image/jpeg" };
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47) return { ext: "png", type: "image/png" };
  if (b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return { ext: "webp", type: "image/webp" };
  return null;
}

export async function onRequestPost({ request, env, data }) {
  if (Number(request.headers.get("Content-Length") || 0) > MAX + 4096) return jsonResponse({ error: "That image is too big." }, 413);
  let form;
  try { form = await request.formData(); } catch { return jsonResponse({ error: "Bad request." }, 400); }
  const file = form.get("file");
  if (!file || typeof file === "string" || !file.size) return jsonResponse({ error: "Choose an image first." }, 400);
  if (file.size > MAX) return jsonResponse({ error: "That image is too big." }, 413);

  const buf = new Uint8Array(await file.arrayBuffer());
  const kind = sniff(buf);
  if (!kind) return jsonResponse({ error: "Use a JPG, PNG or WebP image." }, 400);

  const dim = (v) => { const n = parseInt(v, 10); return n >= 16 && n <= 10000 ? n : 0; };
  const w = dim(form.get("w")), h = dim(form.get("h"));
  const rand = [...crypto.getRandomValues(new Uint8Array(8))].map((x) => x.toString(16).padStart(2, "0")).join("");
  const key = `${new Date().getUTCFullYear()}/${rand}${w && h ? `-${w}x${h}` : ""}.${kind.ext}`;
  await env.MEDIA.put(key, buf, { httpMetadata: { contentType: kind.type }, customMetadata: { by: data.email } });
  return jsonResponse({ url: `/img/blog/${key}`, width: w, height: h }, 201);
}
