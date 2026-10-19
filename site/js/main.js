(function () {
  "use strict";
  var doc = document;
  doc.documentElement.classList.add("js");
  var cfg = window.BF_CONFIG || { jane: { general: "", practitioners: {} } };

  /* ---------- footer year ---------- */
  var yr = doc.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- mobile nav ---------- */
  var toggle = doc.querySelector(".nav-toggle");
  var nav = doc.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    doc.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.closest("a")) setOpen(false);
    });
  }

  /* ---------- Jane App booking links ---------- */
  var jane = cfg.jane || {};
  var people = jane.practitioners || {};
  doc.querySelectorAll("[data-jane]").forEach(function (a) {
    var key = a.getAttribute("data-jane");
    var url = (key !== "general" && people[key]) || jane.general;
    if (!url) return; // keep the on-site fallback href
    a.setAttribute("href", url);
    a.setAttribute("target", "_blank");
    a.setAttribute("rel", "noopener");
  });

  /* ---------- team photo fallback (shows initials if the image file is missing) ---------- */
  doc.querySelectorAll("img[data-fallback]").forEach(function (img) {
    img.addEventListener("error", function () { img.remove(); });
  });

  /* ---------- success story carousel ---------- */
  var carousel = doc.querySelector(".carousel");
  if (carousel) {
    var slides = Array.prototype.slice.call(carousel.querySelectorAll(".story"));
    var dots = Array.prototype.slice.call(carousel.querySelectorAll(".carousel__dot"));
    var idx = 0, timer = null;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var show = function (n) {
      idx = (n + slides.length) % slides.length;
      slides.forEach(function (s, i) {
        var on = i === idx;
        s.classList.toggle("is-active", on);
        s.setAttribute("aria-hidden", on ? "false" : "true");
      });
      dots.forEach(function (d, i) {
        if (i === idx) d.setAttribute("aria-current", "true"); else d.removeAttribute("aria-current");
      });
    };
    var stop = function () { if (timer) { clearInterval(timer); timer = null; } };
    var start = function () {
      if (reduce || timer) return;
      timer = setInterval(function () { show(idx + 1); }, 8000);
    };

    carousel.querySelector(".carousel__prev").addEventListener("click", function () { stop(); show(idx - 1); });
    carousel.querySelector(".carousel__next").addEventListener("click", function () { stop(); show(idx + 1); });
    dots.forEach(function (d, i) { d.addEventListener("click", function () { stop(); show(i); }); });
    carousel.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowLeft") { stop(); show(idx - 1); }
      if (ev.key === "ArrowRight") { stop(); show(idx + 1); }
    });
    carousel.addEventListener("mouseenter", stop);
    carousel.addEventListener("focusin", stop);
    show(0);
    start();
  }

  /* ---------- inquiry forms ---------- */
  doc.querySelectorAll("form[data-inquiry]").forEach(function (form) {
    var status = form.querySelector(".form__status");
    var say = function (msg) { if (status) status.textContent = msg; };

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = String(v).trim(); });

      var bad = null;
      ["name", "email", "message"].forEach(function (k) {
        var el = form.elements[k];
        if (!el) return;
        var ok = data[k] && (k !== "email" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data[k]));
        el.setAttribute("aria-invalid", ok ? "false" : "true");
        if (!ok && !bad) bad = el;
      });
      if (bad) { say("Please fill in your name, a valid email, and a message."); bad.focus(); return; }

      if (cfg.inquiryEndpoint) {
        say("Sending...");
        fetch(cfg.inquiryEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify(data)
        }).then(function (r) {
          if (!r.ok) throw new Error("bad status");
          form.reset();
          say("Thanks, we got your message and will be in touch soon.");
        }).catch(function () {
          say("Something went wrong. Please call 778-766-5083 or email " + cfg.inquiryEmail + ".");
        });
        return;
      }

      // No endpoint configured yet: hand off to the visitor's email app.
      var body = "Name: " + data.name + "\nEmail: " + data.email +
        (data.pathway ? "\nInterested in: " + data.pathway : "") + "\n\n" + data.message;
      var href = "mailto:" + cfg.inquiryEmail + "?subject=" +
        encodeURIComponent("Website inquiry from " + data.name) + "&body=" + encodeURIComponent(body);
      say("Opening your email app to send this...");
      window.location.href = href;
    });
  });
})();
