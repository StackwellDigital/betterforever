/* Better Forever - Google Analytics 4. Loads only on the live domain so demo and preview traffic stays out of the data. */
(function () {
  var ID = "G-21NTYN9TR0";
  var host = location.hostname;
  if (host !== "betterforever.ca" && host !== "www.betterforever.ca") return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", ID);

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);

  /* Conversion events: Jane booking clicks, phone taps, email clicks */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (a.hasAttribute("data-jane")) {
      gtag("event", "jane_click", { practitioner: a.getAttribute("data-jane") || "general", page_path: location.pathname });
    } else if (href.indexOf("tel:") === 0) {
      gtag("event", "phone_click", { page_path: location.pathname });
    } else if (href.indexOf("mailto:") === 0) {
      gtag("event", "email_click", { page_path: location.pathname });
    }
  });
})();
