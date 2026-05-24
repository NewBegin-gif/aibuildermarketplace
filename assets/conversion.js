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
      ts.innerHTML = '<span>✓ Expert-reviewed</span><span>✓ Money-back guarantee</span><span>✓ Cancel anytime</span><span>✓ Trusted by 12k+ founders</span>';
      h1.parentNode.insertBefore(ts, h1.nextSibling);
    }

    // 4. Exit-intent email popup (desktop, once per session)
    if (window.innerWidth > 768 && !sessionStorage.getItem('exit_shown')){
      document.addEventListener('mouseout', function(e){
        if (e.clientY < 10 && !e.relatedTarget && !sessionStorage.getItem('exit_shown')){
          sessionStorage.setItem('exit_shown','1');
          showExit();
        }
      });
    }

    function showExit(){
      var m = document.createElement('div');
      m.id = 'exit-modal';
      m.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;font-family:system-ui,sans-serif';
      m.innerHTML = '<div style="background:#0a0a0a;border:1px solid #333;border-radius:12px;padding:32px;max-width:460px;color:#fff;position:relative">'+
        '<button id="exit-close" style="position:absolute;top:10px;right:12px;background:none;border:none;color:#999;font-size:26px;cursor:pointer;line-height:1">×</button>'+
        '<h3 style="margin:0 0 8px;font-size:22px">Wait — before you go</h3>'+
        '<p style="margin:0 0 18px;color:#bbb;line-height:1.5">Get our free <strong>2026 AI Tool Stack</strong> — 13 hand-picked B2B tools with exclusive partner deals (save $1,200+/yr).</p>'+
        '<form id="exit-form">'+
        '<input type="email" required placeholder="you@startup.com" style="width:100%;box-sizing:border-box;padding:13px;border-radius:8px;border:1px solid #333;background:#1a1a1a;color:#fff;font-size:15px;margin-bottom:10px">'+
        '<button type="submit" style="width:100%;padding:13px;background:#10b981;color:#fff;border:none;border-radius:8px;font-weight:700;font-size:15px;cursor:pointer">Send Me The Guide</button>'+
        '</form>'+
        '<p style="margin:10px 0 0;font-size:11px;color:#666;text-align:center">No spam. Unsubscribe anytime.</p>'+
        '</div>';
      document.body.appendChild(m);
      if (window.gtag) gtag('event','exit_intent_shown',{event_category:'conversion'});
      document.getElementById('exit-close').onclick = function(){ m.remove(); };
      document.getElementById('exit-form').onsubmit = function(ev){
        ev.preventDefault();
        var email = ev.target.querySelector('input').value;
        if (window.gtag) gtag('event','email_signup',{event_category:'conversion',event_label:email});
        ev.target.innerHTML = '<p style="color:#10b981;text-align:center;padding:20px 0">✓ Check your inbox — guide is on its way.</p>';
        setTimeout(function(){ m.remove(); }, 2500);
      };
    }
  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
