/* "Watch this price" — 26 oktober 2026 (Daan 18 okt).
 *
 * Het formulier bij de prijs (build_reviews.prijsalert_html) werkt ook zonder
 * dit bestand: dan is het een gewone POST en antwoordt de API met een
 * HTML-pagina. Dit script maakt er een melding op de pagina zelf van.
 *
 * GA4: price_watch_signup gaat via window.__ga4wacht, de rij van de GA4-poort
 * (/ga4-gate.js), zodat het event pas telt na een echte handeling. Er gaat
 * niets mee dat iemand identificeert: alleen de tool.
 *
 * Geen cookies, geen opslag in de browser, geen derde partij.
 */
(function () {
  var forms = document.querySelectorAll('form[data-price-watch]');
  for (var i = 0; i < forms.length; i++) { koppel(forms[i]); }

  function koppel(f) {
    if (f.__pw) { return; }
    f.__pw = true;
    f.addEventListener('submit', function (e) {
      if (!window.fetch || !window.FormData) { return; }
      e.preventDefault();
      var msg = f.querySelector('[data-price-watch-msg]');
      var knop = f.querySelector('button');
      var data = {};
      new FormData(f).forEach(function (v, k) { data[k] = v; });
      data.page = location.href.split('#')[0].split('?')[0];
      if (knop) { knop.disabled = true; }
      fetch(f.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) {
        return r.json().then(function (j) { return { ok: r.ok, j: j }; });
      }).then(function (res) {
        if (msg) {
          msg.textContent = res.ok ? (res.j.msg || 'Check your inbox to confirm.')
                                   : (res.j.error || 'That did not work. Please try again later.');
          msg.style.color = res.ok ? '#16a34a' : '#dc2626';
        }
        if (res.ok) {
          var tool = data.tool || '';
          (window.__ga4wacht = window.__ga4wacht || []).push(function () {
            if (typeof gtag === 'function') { gtag('event', 'price_watch_signup', { tool: tool }); }
          });
          var veld = f.querySelector('input[type=email]');
          if (veld) { veld.value = ''; }
        }
      }).catch(function () {
        if (msg) { msg.textContent = 'That did not work. Please try again later.'; msg.style.color = '#dc2626'; }
      }).then(function () {
        if (knop) { knop.disabled = false; }
      });
    });
  }
})();
