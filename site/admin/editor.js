(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var today = "";
  var post = null;            // the saved post being edited, or null for a new one
  var dirty = false;
  var slugTouched = false;
  var busy = false;

  /* ---------- api ---------- */
  function api(method, url, body, isForm) {
    var opts = { method: method, credentials: "same-origin", headers: {} };
    if (body && !isForm) { opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
    if (body && isForm) opts.body = body;
    return fetch(url, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) { return { ok: r.ok, status: r.status, data: data }; });
    }).catch(function () {
      return { ok: false, status: 0, data: { error: "Could not reach the site. If you were signed out, reload this page to sign in again." } };
    });
  }

  /* ---------- helpers ---------- */
  function fmtDate(iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) return "";
    return new Date(iso + "T12:00:00Z").toLocaleDateString("en-CA", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
  }
  function slugify(t) {
    return String(t || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80).replace(/-+$/, "");
  }
  function say(msg, isError) {
    var s = $("status");
    s.textContent = msg || "";
    s.classList.toggle("is-error", !!isError);
  }
  function setBusy(on) {
    busy = on;
    ["btn-save", "btn-publish", "btn-unpublish", "btn-delete"].forEach(function (id) { $(id).disabled = on; });
  }
  function stateOf(p) {
    if (!p || p.status !== "published") return "draft";
    return p.published_at > today ? "scheduled" : "live";
  }

  /* ---------- routing ---------- */
  function show(view) {
    $("view-list").hidden = view !== "list";
    $("view-edit").hidden = view !== "edit";
    window.scrollTo(0, 0);
  }
  var currentHash = "#/", ignoreHash = false;
  function route() {
    var h = location.hash || "#/";
    currentHash = h;
    var m;
    if (h === "#/new") return openEditor(null);
    if ((m = /^#\/edit\/(\d+)$/.exec(h))) return loadPost(m[1]);
    return openList();
  }
  function guardedRoute() {
    if (ignoreHash) { ignoreHash = false; return; }
    if (dirty && !confirm("You have changes that are not saved. Leave this page anyway?")) {
      ignoreHash = true;
      location.hash = currentHash;
      return;
    }
    dirty = false;
    route();
  }

  /* ---------- list ---------- */
  function openList() {
    show("list");
    document.title = "Blog admin | Better Forever";
    api("GET", "/api/admin/posts").then(function (r) {
      var ul = $("list");
      ul.textContent = "";
      if (!r.ok) { $("list-empty").hidden = false; $("list-empty").textContent = r.data.error || "Could not load posts."; return; }
      today = r.data.today || today;
      var posts = r.data.posts || [];
      $("list-empty").hidden = posts.length > 0;
      $("list-empty").textContent = "No posts yet. Choose New post to write the first one.";
      posts.forEach(function (p) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.className = "admin-item";
        a.href = "#/edit/" + p.id;
        var left = document.createElement("span");
        var t = document.createElement("span"); t.className = "admin-item__title"; t.textContent = p.title;
        var st = stateOf(p);
        var meta = document.createElement("span"); meta.className = "admin-item__meta";
        meta.textContent = st === "draft" ? "Draft, updated " + fmtDate(String(p.updated_at).slice(0, 10))
          : (st === "scheduled" ? "Goes live " : "Published ") + fmtDate(p.published_at);
        left.appendChild(t); left.appendChild(meta);
        var b = document.createElement("span");
        b.className = "badge" + (st === "live" ? " badge--live" : st === "scheduled" ? " badge--sched" : "");
        b.textContent = st === "live" ? "Live" : st === "scheduled" ? "Scheduled" : "Draft";
        a.appendChild(left); a.appendChild(b); li.appendChild(a); ul.appendChild(li);
      });
    });
  }

  /* ---------- editor ---------- */
  function fill(p) {
    post = p;
    $("f-title").value = p ? p.title : "";
    $("f-slug").value = p ? p.slug : "";
    $("f-date").value = p ? p.published_at : today;
    $("f-excerpt").value = p ? p.excerpt : "";
    $("f-author").value = p ? p.author : "";
    $("f-cover-alt").value = p ? p.cover_alt : "";
    $("f-body").value = p ? p.body_md : "";
    $("ins-alt").value = "";
    $("cover-file").value = ""; $("ins-file").value = "";
    cover = p ? p.cover_url : "";
    slugTouched = !!p;
    renderChrome();
    updateCount();
    setTab("write");
    say("");
    dirty = false;
  }
  var cover = "";

  function renderChrome() {
    var st = stateOf(post);
    var published = post && post.status === "published";
    var b = $("badge");
    b.className = "badge" + (st === "live" ? " badge--live" : st === "scheduled" ? " badge--sched" : "");
    b.textContent = !post ? "New post" : st === "live" ? "Live" : st === "scheduled" ? "Scheduled" : "Draft";
    $("btn-save").textContent = published ? "Save changes" : "Save draft";
    $("btn-publish").hidden = !!published;
    $("btn-unpublish").hidden = !published;
    $("btn-delete").hidden = !post;
    var v = $("btn-view");
    v.hidden = !(post && st === "live");
    // The editor lives on the pages.dev address (Access cannot protect www while its DNS is at GoDaddy), so link to the real site
    if (!v.hidden) v.href = (/\.pages\.dev$/.test(location.hostname) ? "https://www.betterforever.ca" : "") + "/blog/" + post.slug + "/";
    $("f-slug").readOnly = !!published;
    $("slug-hint").textContent = published
      ? "This post is live, so the address is locked. Unpublish it first to change it."
      : "betterforever.ca/blog/" + ($("f-slug").value || "your-address") + "/";
    $("cover-wrap").hidden = !cover;
    $("cover-remove").hidden = !cover;
    if (cover) $("cover-img").src = cover;
    document.title = (post ? "Edit: " + post.title : "New post") + " | Blog admin";
  }

  function openEditor(p) { show("edit"); fill(p); $("f-title").focus(); }
  function loadPost(id) {
    show("edit"); say("Loading...");
    api("GET", "/api/admin/posts/" + id).then(function (r) {
      if (!r.ok) { say(r.data.error || "Could not load that post.", true); return; }
      fill(r.data.post);
    });
  }

  function collect(status) {
    return {
      title: $("f-title").value, slug: $("f-slug").value, published_at: $("f-date").value,
      excerpt: $("f-excerpt").value, author: $("f-author").value, body_md: $("f-body").value,
      cover_url: cover, cover_alt: $("f-cover-alt").value, status: status,
      version: post ? post.version : undefined
    };
  }

  function save(status, doneMsg) {
    if (busy) return;
    if (!$("f-title").value.trim()) { say("Add a title first.", true); $("f-title").focus(); return; }
    if (status === "published" && !$("f-body").value.trim()) { say("Write something before publishing.", true); return; }
    if (status === "published" && cover && !$("f-cover-alt").value.trim() &&
        !confirm("The cover image has no description. Publish anyway?")) return;
    setBusy(true); say("Saving...");
    var req = post ? api("PUT", "/api/admin/posts/" + post.id, collect(status)) : api("POST", "/api/admin/posts", collect(status));
    req.then(function (r) {
      setBusy(false);
      if (!r.ok) { say(r.data.error || "Could not save. Please try again.", true); return; }
      var wasNew = !post;
      post = r.data.post;
      dirty = false;
      $("f-slug").value = post.slug;
      $("f-date").value = post.published_at;
      renderChrome();
      if (wasNew) history.replaceState(null, "", "#/edit/" + post.id);
      var st = stateOf(post);
      say(doneMsg || (status === "published"
        ? (st === "scheduled" ? "Saved. It goes live on " + fmtDate(post.published_at) + "." : "Saved. It is live on the blog.")
        : "Saved."));
    });
  }

  /* ---------- tabs ---------- */
  function setTab(which) {
    var w = which === "write";
    $("tab-write").setAttribute("aria-selected", String(w)); $("tab-write").tabIndex = w ? 0 : -1;
    $("tab-preview").setAttribute("aria-selected", String(!w)); $("tab-preview").tabIndex = w ? -1 : 0;
    $("pane-write").hidden = !w;
    $("pane-preview").hidden = w;
    if (!w) {
      $("preview").textContent = "Loading preview...";
      api("POST", "/api/admin/preview", collect("draft")).then(function (r) {
        // the server returns HTML it generated from escaped text, the same markup the public page uses
        if (r.ok) $("preview").innerHTML = r.data.html; else $("preview").textContent = r.data.error || "Could not build the preview.";
      });
    }
  }

  /* ---------- formatting toolbar ---------- */
  function wrap(before, after, placeholder) {
    var ta = $("f-body"), s = ta.selectionStart, e = ta.selectionEnd;
    var sel = ta.value.slice(s, e) || placeholder;
    ta.setRangeText(before + sel + after, s, e, "end");
    ta.setSelectionRange(s + before.length, s + before.length + sel.length);
    ta.focus(); dirty = true;
  }
  function prefixLines(prefixFn) {
    var ta = $("f-body"), v = ta.value, s = ta.selectionStart, e = ta.selectionEnd;
    var start = v.lastIndexOf("\n", s - 1) + 1;
    var endIdx = v.indexOf("\n", e); if (endIdx === -1) endIdx = v.length;
    var block = v.slice(start, endIdx).split("\n").map(function (l, i) { return prefixFn(i) + l; }).join("\n");
    ta.setRangeText(block, start, endIdx, "end");
    ta.focus(); dirty = true;
  }
  var fmt = {
    bold: function () { wrap("**", "**", "bold text"); },
    italic: function () { wrap("*", "*", "italic text"); },
    heading: function () { prefixLines(function () { return "## "; }); },
    bullets: function () { prefixLines(function () { return "- "; }); },
    numbers: function () { prefixLines(function (i) { return (i + 1) + ". "; }); },
    quote: function () { prefixLines(function () { return "> "; }); },
    link: function () {
      var url = prompt("Where should the link go? Start it with https://");
      if (!url) return;
      if (!/^(https?:\/\/|mailto:|tel:|\/)/.test(url)) url = "https://" + url;
      wrap("[", "](" + url.replace(/\s/g, "") + ")", "link text");
    }
  };

  /* ---------- images ---------- */
  // Resize to 1600px wide and re-encode as JPEG in the browser: small files, and the camera's EXIF data is dropped.
  function prepImage(file) {
    if (!window.createImageBitmap) return Promise.reject(new Error("unsupported"));
    return createImageBitmap(file).then(function (bmp) {
      var scale = Math.min(1, 1600 / bmp.width);
      var w = Math.max(16, Math.round(bmp.width * scale)), h = Math.max(16, Math.round(bmp.height * scale));
      var c = document.createElement("canvas"); c.width = w; c.height = h;
      var ctx = c.getContext("2d");
      ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, w, h);
      ctx.drawImage(bmp, 0, 0, w, h);
      return new Promise(function (res, rej) {
        c.toBlob(function (b) { b ? res({ blob: b, w: w, h: h }) : rej(new Error("encode")); }, "image/jpeg", 0.82);
      });
    });
  }
  function upload(file) {
    say("Uploading picture...");
    return prepImage(file).then(function (img) {
      var fd = new FormData();
      fd.append("file", img.blob, "photo.jpg"); fd.append("w", img.w); fd.append("h", img.h);
      return api("POST", "/api/admin/upload", fd, true);
    }, function () {
      return { ok: false, data: { error: "Could not read that picture. Try a JPG or PNG." } };
    }).then(function (r) {
      if (!r.ok) { say(r.data.error || "Upload failed.", true); return null; }
      say("Picture added.");
      return r.data.url;
    });
  }

  /* ---------- wire up ---------- */
  function init() {
    api("GET", "/api/admin/me").then(function (r) {
      if (r.ok) { $("who").textContent = r.data.email; today = r.data.today || today; }
      route();
    });
    window.addEventListener("hashchange", guardedRoute);
    window.addEventListener("beforeunload", function (ev) { if (dirty) { ev.preventDefault(); ev.returnValue = ""; } });

    $("form").addEventListener("submit", function (ev) { ev.preventDefault(); });
    $("form").addEventListener("input", function (ev) {
      dirty = true;
      if (ev.target.id === "f-title" && !slugTouched && !(post && post.status === "published")) {
        $("f-slug").value = slugify($("f-title").value); renderChrome();
      }
      if (ev.target.id === "f-slug") { slugTouched = true; renderChrome(); }
      if (ev.target.id === "f-excerpt") updateCount();
    });
    $("f-slug").addEventListener("blur", function () { $("f-slug").value = slugify($("f-slug").value); renderChrome(); });

    $("btn-save").addEventListener("click", function () { save(post && post.status === "published" ? "published" : "draft"); });
    $("btn-publish").addEventListener("click", function () { save("published"); });
    $("btn-unpublish").addEventListener("click", function () {
      if (confirm("Take this post off the blog? It will go back to a draft.")) save("draft", "Saved. It is no longer on the blog.");
    });
    $("btn-delete").addEventListener("click", function () {
      if (!post || !confirm("Delete this post for good? This cannot be undone.")) return;
      setBusy(true);
      api("DELETE", "/api/admin/posts/" + post.id).then(function (r) {
        setBusy(false);
        if (!r.ok) { say(r.data.error || "Could not delete.", true); return; }
        dirty = false; location.hash = "#/";
      });
    });
    document.addEventListener("keydown", function (ev) {
      if ((ev.ctrlKey || ev.metaKey) && ev.key === "s" && !$("view-edit").hidden) {
        ev.preventDefault();
        save(post && post.status === "published" ? "published" : "draft");
      }
    });

    $("tab-write").addEventListener("click", function () { setTab("write"); });
    $("tab-preview").addEventListener("click", function () { setTab("preview"); });
    document.querySelector(".admin-tabs").addEventListener("keydown", function (ev) {
      if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
      var toPreview = ev.key === "ArrowRight";
      setTab(toPreview ? "preview" : "write"); $(toPreview ? "tab-preview" : "tab-write").focus();
    });

    document.querySelector(".toolbar").addEventListener("click", function (ev) {
      var b = ev.target.closest("button[data-fmt]");
      if (b && fmt[b.getAttribute("data-fmt")]) fmt[b.getAttribute("data-fmt")]();
    });

    $("cover-file").addEventListener("change", function (ev) {
      var f = ev.target.files[0]; if (!f) return;
      upload(f).then(function (url) { if (url) { cover = url; dirty = true; renderChrome(); $("f-cover-alt").focus(); } ev.target.value = ""; });
    });
    $("cover-remove").addEventListener("click", function () { cover = ""; dirty = true; renderChrome(); });

    $("ins-file").addEventListener("change", function (ev) {
      var f = ev.target.files[0]; if (!f) return;
      var alt = $("ins-alt").value.trim();
      if (!alt) { say("Describe the picture first, then choose it again.", true); $("ins-alt").focus(); ev.target.value = ""; return; }
      upload(f).then(function (url) {
        ev.target.value = "";
        if (!url) return;
        var ta = $("f-body"), pos = ta.selectionStart;
        var md = "\n\n![" + alt.replace(/[\[\]]/g, "") + "](" + url + ")\n\n";
        ta.setRangeText(md, pos, pos, "end"); $("ins-alt").value = ""; dirty = true;
      });
    });
  }
  function updateCount() { $("excerpt-count").textContent = String($("f-excerpt").value.length); }

  init();
})();
