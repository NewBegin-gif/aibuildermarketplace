/*!
 * AIBuilder Marketplace — Shortlist (vanilla JS + localStorage)
 * Ster-knop op elke kaart (.shortlist-btn[data-name]) → bewaart tools in
 * localStorage → zwevende "Shortlist (N)"-badge → slide-over met de bewaarde
 * tools + hun affiliate-CTA. Standalone, scoped CSS, werkt op elk domein.
 * Leest link/logo uit de kaart zelf, dus de knop hoeft alleen data-name.
 */
(function () {
  "use strict";
  var KEY = "aibm_shortlist";
  var PREFIX = /^(www|try|get|go|join|start|now|refer|partners?|affiliates?|psref)\./;

  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (_) { return []; } }
  function save(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (_) {} }
  function has(a, n) { return a.some(function (x) { return x.name === n; }); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function cardInfo(btn) {
    var card = btn.closest(".tool-card");
    var link = "", domain = "";
    if (card) {
      var a = card.querySelector('a[rel~="sponsored"][href^="http"]');
      if (a) link = a.href;
      var img = card.querySelector("img[src]");
      if (img) { var m = /(?:clearbit\.com\/|domain=)([^&"?]+)/.exec(img.getAttribute("src") || ""); if (m) domain = m[1]; }
    }
    return { link: link, domain: domain };
  }

  function injectCSS() {
    if (document.getElementById("sl-css")) return;
    var s = document.createElement("style"); s.id = "sl-css";
    s.textContent = [
      ".shortlist-btn{background:transparent;border:0;cursor:pointer;color:#94a3b8;font-size:1.15rem;line-height:1;padding:4px 6px;border-radius:6px;flex:0 0 auto;transition:color .15s,transform .15s}",
      ".shortlist-btn:hover{color:#f1f5f9;transform:scale(1.15)}",
      ".shortlist-btn.on{color:#f59e0b}",
      "#sl-badge{position:fixed;right:18px;bottom:18px;z-index:9997;background:#6366f1;color:#fff;border:0;border-radius:999px;padding:11px 18px;font:700 .9rem Inter,system-ui,sans-serif;cursor:pointer;box-shadow:0 6px 22px rgba(0,0,0,.4);display:none}",
      "#sl-over{position:fixed;inset:0;z-index:9998;background:rgba(2,6,23,.6);display:none}",
      "#sl-panel{position:fixed;top:0;right:0;height:100%;width:min(420px,92vw);background:#0f1422;border-left:1px solid #1e293b;box-shadow:-10px 0 40px rgba(0,0,0,.5);transform:translateX(100%);transition:transform .3s ease;display:flex;flex-direction:column;font-family:Inter,system-ui,sans-serif}",
      "#sl-over.open #sl-panel{transform:translateX(0)}",
      "#sl-panel h3{margin:0;padding:20px;font-size:1.1rem;color:#f1f5f9;border-bottom:1px solid #1e293b;display:flex;justify-content:space-between;align-items:center}",
      "#sl-x{background:none;border:0;color:#94a3b8;font-size:1.5rem;cursor:pointer;line-height:1}",
      "#sl-list{flex:1;overflow:auto;padding:14px 16px;display:flex;flex-direction:column;gap:10px}",
      ".sl-item{display:flex;align-items:center;gap:11px;background:#1a1f2e;border:1px solid #1e293b;border-radius:11px;padding:11px 13px}",
      ".sl-item img{width:34px;height:34px;border-radius:8px;background:#fff;padding:4px;flex:0 0 auto}",
      ".sl-item .sl-n{font-weight:700;color:#f1f5f9;font-size:.92rem;flex:1}",
      ".sl-item a{background:#6366f1;color:#fff;text-decoration:none;font-weight:700;font-size:.8rem;padding:7px 12px;border-radius:8px;white-space:nowrap}",
      ".sl-item .sl-rm{background:none;border:0;color:#64748b;cursor:pointer;font-size:1.1rem;line-height:1}",
      ".sl-empty{color:#64748b;text-align:center;padding:40px 16px;font-size:.9rem}"
    ].join("");
    document.head.appendChild(s);
  }

  function buildWidget() {
    if (document.getElementById("sl-badge")) return;
    var badge = document.createElement("button");
    badge.id = "sl-badge"; badge.type = "button";
    badge.addEventListener("click", function () { document.getElementById("sl-over").classList.add("open"); document.getElementById("sl-over").style.display = "block"; });
    document.body.appendChild(badge);
    var over = document.createElement("div"); over.id = "sl-over";
    over.innerHTML = '<div id="sl-panel"><h3>Your shortlist <button id="sl-x" aria-label="Close">&times;</button></h3><div id="sl-list"></div></div>';
    document.body.appendChild(over);
    function close() { over.classList.remove("open"); setTimeout(function () { over.style.display = "none"; }, 300); }
    over.addEventListener("click", function (e) { if (e.target === over) close(); });
    over.querySelector("#sl-x").addEventListener("click", close);
  }

  function render() {
    var a = load(), badge = document.getElementById("sl-badge"), list = document.getElementById("sl-list");
    if (badge) { badge.textContent = "★ Shortlist (" + a.length + ")"; badge.style.display = a.length ? "block" : "none"; }
    if (list) {
      list.innerHTML = a.length ? a.map(function (t) {
        var fav = t.domain ? '<img src="https://logo.clearbit.com/' + esc(t.domain) + '" alt="" onerror="this.style.visibility=\'hidden\'">' : "";
        return '<div class="sl-item">' + fav + '<span class="sl-n">' + esc(t.name) + '</span>' +
          (t.link ? '<a href="' + esc(t.link) + '" target="_blank" rel="sponsored noopener nofollow">Visit →</a>' : "") +
          '<button class="sl-rm" data-name="' + esc(t.name) + '" aria-label="Remove">&times;</button></div>';
      }).join("") : '<div class="sl-empty">No tools saved yet. Tap the ☆ on any tool to build your shortlist.</div>';
    }
  }

  function toggle(btn) {
    var a = load(), name = btn.dataset.name;
    if (has(a, name)) a = a.filter(function (x) { return x.name !== name; });
    else { var info = cardInfo(btn); a.push({ name: name, link: info.link, domain: info.domain }); }
    save(a); syncBtns(); render();
  }

  function syncBtns() {
    var a = load();
    document.querySelectorAll(".shortlist-btn").forEach(function (b) {
      var on = has(a, b.dataset.name);
      b.classList.toggle("on", on); b.textContent = on ? "★" : "☆";
      b.setAttribute("aria-label", (on ? "Remove from" : "Save to") + " shortlist");
    });
  }

  function mount() {
    injectCSS(); buildWidget();
    document.querySelectorAll(".shortlist-btn").forEach(function (b) {
      if (b.dataset.slBound) return; b.dataset.slBound = "1";
      b.addEventListener("click", function (e) { e.stopPropagation(); e.preventDefault(); toggle(b); });
    });
    document.addEventListener("click", function (e) {
      var rm = e.target && e.target.closest ? e.target.closest(".sl-rm") : null;
      if (rm) { var a = load().filter(function (x) { return x.name !== rm.dataset.name; }); save(a); syncBtns(); render(); }
    });
    syncBtns(); render();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount); else mount();
  window.aibmShortlist = { mount: mount };
})();
