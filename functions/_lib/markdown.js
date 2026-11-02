// Small, safe markdown renderer for blog posts.
// Raw HTML is never passed through: everything is escaped first, then a fixed set of tags is generated.
// Supported: ## headings, paragraphs, **bold**, *italic*, [links](https://...), lists, > quotes, --- rules,
// and images that were uploaded through the admin (/img/blog/...). A single line break becomes <br>.

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ESC[c]);

const SAFE_IMG = /^\/img\/blog\/[A-Za-z0-9/_.-]+$/;
const SAFE_HREF = /^(https?:\/\/[^\s"'<>*]+|mailto:[^\s"'<>*]+|tel:[+0-9().-]+|\/(?!\/)[^\s"'<>*]*|#[^\s"'<>*]*)$/;

// Uploads are named like 2026/ab12cd34ef56-1600x900.jpg so width and height can be set without a lookup.
export function imgSize(url) {
  const m = /-(\d{2,5})x(\d{2,5})\.[a-z]+$/.exec(url);
  return m ? { w: +m[1], h: +m[2] } : null;
}

export function imgTag(url, alt, extra = "") {
  const d = imgSize(url);
  const size = d ? ` width="${d.w}" height="${d.h}"` : "";
  return `<img src="${esc(url)}" alt="${esc(alt)}"${size}${extra} loading="lazy" decoding="async">`;
}

const emph = (t) =>
  t.replace(/\*\*([^*\n]+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, "$1<em>$2</em>");

function inline(raw) {
  // Generated tags go into a stash while the rest is escaped, so escaping happens exactly once
  // and emphasis can never reach inside an attribute.
  const stash = [];
  const hold = (html) => `\u0000${stash.push(html) - 1}\u0000`;
  let t = String(raw).replace(/\u0000/g, "");
  t = t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (m, alt, url) =>
    SAFE_IMG.test(url) ? hold(imgTag(url, alt.replace(/\*/g, ""))) : alt);
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, text, url) => {
    if (!SAFE_HREF.test(url)) return text;
    const rel = /^https?:/.test(url) ? ' rel="noopener noreferrer"' : "";
    return hold(`<a href="${esc(url)}"${rel}>${emph(esc(text))}</a>`);
  });
  t = emph(esc(t));
  for (let n = 0; n < 3 && /\u0000\d+\u0000/.test(t); n++) t = t.replace(/\u0000(\d+)\u0000/g, (_, k) => stash[+k]);
  return t;
}

const reHead = /^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$/;
const reHr = /^\s{0,3}([-*_])(\s*\1){2,}\s*$/;
const reQuote = /^\s{0,3}>/;
const reUl = /^\s{0,3}[-*+]\s+(.*)$/;
const reOl = /^\s{0,3}\d{1,3}[.)]\s+(.*)$/;
const blank = (l) => /^\s*$/.test(l);
const startsBlock = (l) => reHead.test(l) || reHr.test(l) || reQuote.test(l) || reUl.test(l) || reOl.test(l);

export function renderMarkdown(src, depth = 0) {
  const lines = String(src ?? "").replace(/\r\n?/g, "\n").split("\n");
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (blank(line)) { i++; continue; }
    let m;

    if ((m = reHead.exec(line))) {
      const lvl = m[1].length <= 2 ? 2 : 3; // the post title is the h1
      out.push(`<h${lvl}>${inline(m[2])}</h${lvl}>`);
      i++; continue;
    }
    if (reHr.test(line)) { out.push("<hr>"); i++; continue; }

    if (reQuote.test(line) && depth < 3) {
      const buf = [];
      while (i < lines.length && reQuote.test(lines[i])) { buf.push(lines[i].replace(/^\s{0,3}>\s?/, "")); i++; }
      out.push(`<blockquote>${renderMarkdown(buf.join("\n"), depth + 1)}</blockquote>`);
      continue;
    }

    if (reUl.test(line) || reOl.test(line)) {
      const ordered = !reUl.test(line);
      const re = ordered ? reOl : reUl;
      const items = [];
      while (i < lines.length && (m = re.exec(lines[i]))) {
        let text = m[1]; i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !re.test(lines[i])) { text += "\n" + lines[i].trim(); i++; }
        items.push(text);
        if (i + 1 < lines.length && blank(lines[i]) && re.test(lines[i + 1])) i++; // one blank line between items is fine
      }
      const tag = ordered ? "ol" : "ul";
      out.push(`<${tag}>` + items.map((t) => `<li>${inline(t).replace(/\n/g, "<br>")}</li>`).join("") + `</${tag}>`);
      continue;
    }

    const buf = [line]; i++;
    while (i < lines.length && !blank(lines[i]) && !startsBlock(lines[i])) { buf.push(lines[i]); i++; }
    const html = buf.map((l) => inline(l.trim()));
    if (buf.length === 1 && html[0].startsWith("<img ") && html[0].endsWith(">") && html[0].indexOf("<", 1) === -1) {
      out.push(`<figure class="post__figure">${html[0]}</figure>`);
    } else {
      out.push(`<p>${html.join("<br>")}</p>`);
    }
  }
  return out.join("\n");
}

// Plain text version, used to build a summary when none was written.
export function markdownToText(md) {
  return String(md ?? "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/^\s{0,3}(#{1,6}|>|[-*+]|\d{1,3}[.)])\s+/gm, "")
    .replace(/[*_`]+/g, "")
    .replace(/\s+/g, " ")
    .trim();
}
