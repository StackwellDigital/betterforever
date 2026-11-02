// Cloudflare Access JWT check for /admin and /api/admin.
// Access sits at the edge, and this verifies the signed token again so the origin never trusts the edge alone.
// Fails closed: if ACCESS_TEAM_DOMAIN or ACCESS_AUD is missing, every admin request is refused.

let certCache = { at: 0, team: "", keys: [] };

const b64urlBytes = (s) => {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  s += "=".repeat((4 - (s.length % 4)) % 4);
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
};
const b64urlJson = (s) => JSON.parse(new TextDecoder().decode(b64urlBytes(s)));

async function getKeys(team, force, fetchFn) {
  if (!force && certCache.team === team && Date.now() - certCache.at < 3600_000) return certCache.keys;
  const r = await fetchFn(`https://${team}/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error("certs unavailable");
  const j = await r.json();
  certCache = { at: Date.now(), team, keys: j.keys || [] };
  return certCache.keys;
}

export function normalizeTeam(t) {
  return String(t || "").trim().replace(/^https?:\/\//, "").replace(/\/+$/, "").toLowerCase();
}

export async function verifyAccessJwt(token, { team, aud, fetchFn = fetch, nowMs = Date.now() }) {
  const parts = String(token || "").split(".");
  if (parts.length !== 3) throw new Error("malformed");
  const header = b64urlJson(parts[0]);
  const claims = b64urlJson(parts[1]);
  if (header.alg !== "RS256" || !header.kid) throw new Error("alg");

  let keys = await getKeys(team, false, fetchFn);
  let jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) {
    keys = await getKeys(team, true, fetchFn); // keys rotate: refetch once on unknown kid
    jwk = keys.find((k) => k.kid === header.kid);
  }
  if (!jwk) throw new Error("kid");

  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const ok = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5", key, b64urlBytes(parts[2]), new TextEncoder().encode(parts[0] + "." + parts[1]));
  if (!ok) throw new Error("signature");

  const now = Math.floor(nowMs / 1000);
  if (claims.iss !== `https://${team}`) throw new Error("iss");
  const auds = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  const allowed = String(aud).split(",").map((a) => a.trim()).filter(Boolean);
  if (!auds.some((a) => allowed.includes(a))) throw new Error("aud");
  if (typeof claims.exp !== "number" || claims.exp < now - 30) throw new Error("exp");
  if (typeof claims.nbf === "number" && claims.nbf > now + 30) throw new Error("nbf");
  if (typeof claims.email !== "string" || !claims.email) throw new Error("email");
  return { email: claims.email.toLowerCase() };
}

const deny = (status, msg) =>
  new Response(msg, { status, headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } });

// Returns { email } or a Response to send back.
export async function requireAccess(request, env) {
  const host = new URL(request.url).hostname;
  // Local development only: wrangler pages dev on localhost with DEV_AUTH_EMAIL in .dev.vars
  if (env.DEV_AUTH_EMAIL && (host === "localhost" || host === "127.0.0.1")) return { email: env.DEV_AUTH_EMAIL };

  const team = normalizeTeam(env.ACCESS_TEAM_DOMAIN);
  if (!team || !env.ACCESS_AUD) return deny(503, "Admin is not configured yet.");

  let token = request.headers.get("Cf-Access-Jwt-Assertion");
  if (!token) token = (request.headers.get("Cookie") || "").match(/(?:^|;\s*)CF_Authorization=([^;]+)/)?.[1];
  if (!token) return deny(403, "Sign in required.");
  try {
    return await verifyAccessJwt(token, { team, aud: env.ACCESS_AUD });
  } catch {
    return deny(403, "Sign in required.");
  }
}
