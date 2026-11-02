// Everything under /admin/ (the editor page and its files) needs a valid Cloudflare Access login.
import { requireAccess } from "../_lib/auth.js";

export async function onRequest({ request, env, next }) {
  const a = await requireAccess(request, env);
  if (a instanceof Response) return a;
  const res = await next();
  const h = new Headers(res.headers);
  h.set("Cache-Control", "no-store");
  h.set("X-Robots-Tag", "noindex, nofollow");
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
}
