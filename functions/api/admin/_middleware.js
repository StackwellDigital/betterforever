// Everything under /api/admin/ needs a valid Cloudflare Access login, and writes must come from this site.
import { requireAccess } from "../../_lib/auth.js";
import { jsonResponse } from "../../_lib/blog.js";

export async function onRequest({ request, env, data, next }) {
  const a = await requireAccess(request, env);
  if (a instanceof Response) return a;
  data.email = a.email;

  if (request.method !== "GET" && request.method !== "HEAD") {
    let ok = false;
    try { ok = new URL(request.headers.get("Origin") || "").host === new URL(request.url).host; } catch {}
    if (!ok) return jsonResponse({ error: "Request blocked." }, 403);
  }
  try {
    return await next();
  } catch (err) {
    console.error("admin api", err && err.message);
    return jsonResponse({ error: "Something went wrong. Please try again." }, 500);
  }
}
