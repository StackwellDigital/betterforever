// Cloudflare Pages Function: POST /api/inquiry
// Secret: RESEND_API_KEY (send-only key, Pages > Settings > Variables and Secrets)
const TO = "info@betterforever.ca";
const FROM = "Better Forever Website <forms@betterforever.ca>";
const MAX = { name: 100, email: 150, pathway: 100, message: 4000 };

const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

export async function onRequestPost({ request, env }) {
  const origin = request.headers.get("Origin") || "";
  const host = new URL(request.url).host;
  if (origin && new URL(origin).host !== host) return json({ ok: false }, 403);
  if (!env.RESEND_API_KEY) return json({ ok: false, error: "not configured" }, 500);

  let d;
  try { d = await request.json(); } catch { return json({ ok: false }, 400); }

  // Honeypot: silently accept bots
  if (d.website || d.company) return json({ ok: true });

  const f = {};
  for (const k of Object.keys(MAX)) f[k] = String(d[k] ?? "").trim().slice(0, MAX[k]);
  if (!f.name || !f.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email)) return json({ ok: false }, 400);
  if (/[\r\n]/.test(f.name + f.email)) return json({ ok: false }, 400);

  const text = `Name: ${f.name}\nEmail: ${f.email}\n${f.pathway ? "Interested in: " + f.pathway + "\n" : ""}\n${f.message}`;
  const html = `<p><b>Name:</b> ${esc(f.name)}<br><b>Email:</b> ${esc(f.email)}<br>${f.pathway ? "<b>Interested in:</b> " + esc(f.pathway) + "<br>" : ""}</p><p>${esc(f.message).replace(/\n/g, "<br>")}</p>`;

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": "Bearer " + env.RESEND_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: FROM,
      to: [TO],
      reply_to: f.email,
      subject: "Website inquiry from " + f.name,
      text,
      html
    })
  });
  return r.ok ? json({ ok: true }) : json({ ok: false }, 502);
}

export const onRequest = ({ request }) =>
  request.method === "POST" ? undefined : new Response("Method not allowed", { status: 405, headers: { Allow: "POST" } });
