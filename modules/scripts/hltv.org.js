(function () {
  const response = typeof $response !== "undefined" ? $response : {};
  const request = typeof $request !== "undefined" ? $request : {};
  const body = response.body || "";
  const requestUrl = request.url || "";

  if (!/^https?:\/\/(?:www\.)?hltv\.org(?:\/|$)/i.test(requestUrl)) {
    $done({});
    return;
  }

  if (!body || typeof body !== "string") {
    $done({});
    return;
  }

  const headers = Object.assign({}, response.headers || {});
  const contentTypeKey = Object.keys(headers).find((key) => /^content-type$/i.test(key));
  const contentType = contentTypeKey ? headers[contentTypeKey] : "";
  const isHtml = /html/i.test(contentType) || /<html[\s>]/i.test(body);

  if (!isHtml) {
    $done({});
    return;
  }

  if (body.includes("surge-hltv-ad-cleaner")) {
    $done({ headers, body });
    return;
  }

  for (const key of Object.keys(headers)) {
    if (/^content-security-policy$/i.test(key) || /^x-content-security-policy$/i.test(key) || /^content-length$/i.test(key)) {
      delete headers[key];
    }
  }

  const injection = `
<style id="surge-hltv-ad-cleaner">
html body {
  background-image: none !important;
  background-attachment: initial !important;
}

.logoCon > *:not(:first-child),
#betting,
[class*="bg-sidebar"],
[class*="background-ad"],
[class*="skin-ad"],
[class*="ad-container"],
[class*="adContainer"],
[class*="ad-unit"],
[class*="adUnit"],
[class*="advertisement"],
[class*="banner"],
[class*="sponsor"],
[class*="yabo"],
iframe[src*="adform"],
iframe[src*="doubleclick"],
iframe[src*="googlesyndication"],
iframe[src*="googleadservices"],
iframe[src*="smartadserver"],
iframe[src*="rubiconproject"],
iframe[src*="pubmatic"],
a[href^="http"][href*="casino"]:not([href*="hltv.org"]),
a[href^="http"][href*="gambling"]:not([href*="hltv.org"]),
a[href^="http"][href*="gg.bet"]:not([href*="hltv.org"]),
a[href^="http"][href*="stake"]:not([href*="hltv.org"]),
a[href^="http"][href*="yabo"]:not([href*="hltv.org"]),
a[href^="http"][href*="1xbet"]:not([href*="hltv.org"]),
a[href^="http"][href*="bet365"]:not([href*="hltv.org"]),
a[href^="http"][href*="csgoempire"]:not([href*="hltv.org"]),
a[href^="http"][href*="csgoroll"]:not([href*="hltv.org"]),
a[href^="http"][href*="gamdom"]:not([href*="hltv.org"]),
a[href^="http"][href*="rollbit"]:not([href*="hltv.org"]) {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}
</style>
<script id="surge-hltv-ad-cleaner-js">
(function () {
  var adHrefPattern = /(casino|gambling|gg\\.bet|stake|yabo|1xbet|bet365|csgoempire|csgoroll|gamdom|rollbit)/i;

  function hideElement(element) {
    if (!element || !element.style) return;
    element.style.setProperty("display", "none", "important");
    element.style.setProperty("visibility", "hidden", "important");
    element.style.setProperty("pointer-events", "none", "important");
  }

  function cleanBodySkin() {
    if (!document.body) return;
    document.body.removeAttribute("data-href");
    document.body.style.removeProperty("background");
    document.body.style.removeProperty("background-image");
    document.body.style.removeProperty("background-attachment");
    document.body.style.cursor = "auto";
  }

  function cleanTopAds() {
    var logo = document.querySelector(".logoCon");
    if (!logo || logo.children.length < 2) return;
    Array.prototype.slice.call(logo.children, 1).forEach(hideElement);
  }

  function cleanAdLinks() {
    document.querySelectorAll("a[href^='http']").forEach(function (link) {
      var href = link.getAttribute("href") || "";
      if (/hltv\\.org/i.test(href)) return;
      if (adHrefPattern.test(href)) hideElement(link);
    });
  }

  function clean() {
    cleanBodySkin();
    cleanTopAds();
    cleanAdLinks();
  }

  clean();
  var timer = setInterval(clean, 300);
  setTimeout(function () {
    clearInterval(timer);
  }, 6000);

  if (window.MutationObserver) {
    new MutationObserver(clean).observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["style", "data-href"]
    });
  }

  console.log("[HLTV Surge] ad cleanup injected");
})();
</script>`;

  let nextBody = body.replace(/<\/head>/i, injection + "\n</head>");
  if (nextBody === body) {
    nextBody = body.replace(/<\/body>/i, injection + "\n</body>");
  }
  if (nextBody === body) {
    nextBody = injection + body;
  }

  $done({ headers, body: nextBody });
})();
