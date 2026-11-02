// GET /img/blog/<year>/<id>.jpg : blog images from R2, same origin so the CSP stays img-src 'self'.
const KEY = /^\d{4}\/[a-f0-9]{16}(?:-\d{2,5}x\d{2,5})?\.(?:jpg|png|webp)$/;

export async function onRequestGet({ request, env, params }) {
  const key = Array.isArray(params.path) ? params.path.join("/") : String(params.path || "");
  if (!KEY.test(key)) return new Response("Not found", { status: 404 });
  const obj = await env.MEDIA.get(key);
  if (!obj) return new Response("Not found", { status: 404 });
  const etag = obj.httpEtag;
  const h = new Headers({
    "Content-Type": obj.httpMetadata?.contentType || "application/octet-stream",
    "Cache-Control": "public, max-age=31536000, immutable",
    "X-Content-Type-Options": "nosniff",
    ETag: etag,
  });
  if (request.headers.get("If-None-Match") === etag) return new Response(null, { status: 304, headers: h });
  return new Response(request.method === "HEAD" ? null : obj.body, { headers: h });
}
export const onRequestHead = onRequestGet;
