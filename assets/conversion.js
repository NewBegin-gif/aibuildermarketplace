/* AIBuilder Marketplace — Conversion Toolkit v1 */
(function(){
  if (window.__convtkit) return;
  window.__convtkit = true;
  if (document.body && document.body.dataset.skipConv === '1') return;

  // ===== Brand list (same as click-tracker) =====
  var BRANDS = ['kinsta.com','beehiiv','bitvavo','synthesia','invideo','replit','clay.com','murf.ai','wp-rocket','rankmath','jotform','chemicloud','frase.io','hostinger'];

  function init(){
    // 1. Find first affiliate link as primary CTA
    var ctaLink = null;
    for (var i=0;i<BRANDS.length;i++){
      var a = document.querySelector('a[href*="'+BRANDS[i]+'"]');
      if (a){ ctaLink = a.href; break; }
    }

    // 2. Sticky mobile CTA bar
    if (ctaLink && window.innerWidth <= 768){
      var bar = document.createElement('div');
      bar.id = 'mobile-cta-bar';
      bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;border-top:1px solid #333;padding:10px 14px;z-index:9999;box-shadow:0 -4px 12px rgba(0,0,0,0.4);display:flex;align-items:center;gap:10px;font-family:system-ui,sans-serif';
      bar.innerHTML = '<div style="flex:1;color:#fff;font-size:12px;line-height:1.3"><strong>Best Deal 2026</strong><br><span style="opacity:0.7">Exclusive partner discount</span></div>'+
        '<a href="'+ctaLink+'" target="_blank" rel="nofollow sponsored" id="mobile-cta-btn" style="background:#10b981;color:#fff;padding:12px 16px;border-radius:8px;text-decoration:none;font-weight:700;font-size:13px;white-space:nowrap">Get Deal →</a>';
      document.body.appendChild(bar);
      document.body.style.paddingBottom = '80px';
      document.getElementById('mobile-cta-btn').addEventListener('click', function(){
        if (window.gtag) gtag('event','sticky_cta_click',{event_category:'conversion',event_label:ctaLink});
      });
    }

    // 3. Trust strip after first <h1>
    var h1 = document.querySelector('main h1, article h1, h1');
    if (h1 && !document.getElementById('trust-strip')){
      var ts = document.createElement('div');
      ts.id = 'trust-strip';
      ts.style.cssText = 'display:flex;gap:12px;flex-wrap:wrap;margin:14px 0 22px;padding:10px 14px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);border-radius:8px;font-size:13px;color:#10b981;font-family:system-ui,sans-serif';
      ts.innerHTML = '<span>✓ Expert-reviewed</span>';
      h1.parentNode.insertBefore(ts, h1.nextSibling);
    }

  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
