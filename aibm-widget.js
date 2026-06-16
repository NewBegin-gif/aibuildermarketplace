/*!
 * AIBuilder Marketplace embed-widget — aibm-widget.js
 * Plak op elke pagina (ook externe blogs):
 *   <div class="aibm-widget" data-tool="Clay"></div>
 *   <script async src="https://aibuildermarketplace.com/aibm-widget.js"></script>
 * Rendert een live affiliate-kaart uit de centrale data.json. Eén bron, overal
 * bijgewerkt. Vanilla JS, geen dependencies, scoped styling. Vuurt het GA4
 * affiliate_click-event (partner + source=widget) zodat blog-conversies meetellen.
 */
(function () {
  "use strict";
  var DATA_URL = "https://aibuildermarketplace.com/widget-data.json";
  var SITE = "https://aibuildermarketplace.com";
  var GA_ID = "G-CW1KZ258ZV";
  var PREFIX = /^(www|try|get|go|join|start|now|refer|partners?|affiliates?|psref)\./;

  // ---- GA4 (één keer laden; werkt ook op externe domeinen) ----
  function ensureGtag() {
    if (window.gtag) return;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    // anonieme config: meet alleen het event, geen page_views op de blog
    window.gtag("config", GA_ID, { send_page_view: false });
  }
  function partnerOf(link) {
    try { return (new URL(link).hostname || "").replace(PREFIX, ""); }
    catch (e) { return ""; }
  }
  function track(tool) {
    try {
      ensureGtag();
      window.gtag("event", "affiliate_click", {
        partner: partnerOf(tool.link),
        source: "widget",
        embed_host: location.hostname,
        tool: tool.name
      });
    } catch (e) {}
  }

  // ---- styling (één keer, scoped onder .aibm-widget) ----
  function injectCSS() {
    if (document.getElementById("aibm-widget-css")) return;
    var css = document.createElement("style");
    css.id = "aibm-widget-css";
    css.textContent = [
      ".aibm-widget{all:initial;display:block;max-width:420px;margin:18px 0;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}",
      ".aibm-w-card{background:#1a1f2e;border:1px solid #1e293b;border-radius:14px;padding:20px;color:#f1f5f9;box-sizing:border-box}",
      ".aibm-w-top{display:flex;align-items:center;gap:12px;margin-bottom:12px}",
      ".aibm-w-logo{width:44px;height:44px;border-radius:10px;background:#fff;flex:0 0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;font-weight:800;color:#1e293b;font-size:1.1rem}",
      ".aibm-w-logo img{width:100%;height:100%;object-fit:contain;padding:5px;box-sizing:border-box}",
      ".aibm-w-name{font-size:1.1rem;font-weight:700;line-height:1.2;color:#f1f5f9;margin:0}",
      ".aibm-w-cat{font-size:.72rem;font-weight:600;color:#6366f1;margin-top:3px}",
      ".aibm-w-desc{font-size:.9rem;line-height:1.55;color:#94a3b8;margin:0 0 16px}",
      ".aibm-w-cta{display:block;text-align:center;background:#6366f1;color:#fff !important;text-decoration:none;padding:11px 18px;border-radius:9px;font-weight:700;font-size:.92rem}",
      ".aibm-w-cta:hover{opacity:.9}",
      ".aibm-w-foot{display:block;text-align:center;margin-top:10px;font-size:.72rem;color:#64748b !important;text-decoration:none}",
      ".aibm-w-foot:hover{color:#94a3b8 !important}"
    ].join("");
    document.head.appendChild(css);
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function render(el, tool) {
    var letter = tool.name.charAt(0).toUpperCase();
    el.innerHTML =
      '<div class="aibm-w-card">' +
      '<div class="aibm-w-top">' +
      '<div class="aibm-w-logo" data-l="' + esc(letter) + '">' +
      '<img src="https://logo.clearbit.com/' + esc(tool.domain) + '" alt="' + esc(tool.name) + '" ' +
      'onerror="if(!this.dataset.t){this.dataset.t=1;this.src=\'https://www.google.com/s2/favicons?domain=' + esc(tool.domain) + '&sz=128\'}else{this.parentNode.textContent=this.parentNode.dataset.l}">' +
      '</div>' +
      '<div><p class="aibm-w-name">' + esc(tool.name) + '</p>' +
      '<div class="aibm-w-cat">' + esc(tool.category) + '</div></div>' +
      '</div>' +
      '<p class="aibm-w-desc">' + esc(tool.desc) + '</p>' +
      '<a class="aibm-w-cta" href="' + esc(tool.link) + '" target="_blank" rel="sponsored noopener nofollow">Visit ' + esc(tool.name) + ' &rarr;</a>' +
      '<a class="aibm-w-foot" href="' + SITE + '/b2b/?tool=' + encodeURIComponent(tool.name) + '" target="_blank" rel="noopener">Compare &amp; reviews via AIBuilder Marketplace</a>' +
      '</div>';
    var cta = el.querySelector(".aibm-w-cta");
    if (cta) cta.addEventListener("click", function () { track(tool); });
  }

  var cache = null;
  function load() {
    if (!cache) cache = fetch(DATA_URL, { cache: "default" }).then(function (r) { return r.json(); });
    return cache;
  }
  function norm(s) { return String(s || "").toLowerCase().replace(/[^a-z0-9]/g, ""); }

  function mount() {
    var nodes = document.querySelectorAll(".aibm-widget[data-tool]:not([data-aibm-done])");
    if (!nodes.length) return;
    injectCSS();
    load().then(function (data) {
      var byKey = {};
      data.forEach(function (t) { byKey[t.key || norm(t.name)] = t; });
      nodes.forEach(function (el) {
        el.setAttribute("data-aibm-done", "1");
        var tool = byKey[norm(el.getAttribute("data-tool"))];
        if (tool) render(el, tool);
        else el.style.display = "none";
      });
    }).catch(function () {});
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
  // her-mount voor dynamisch ingeladen content (blogs, SPA's)
  window.aibmWidget = { mount: mount };
})();
