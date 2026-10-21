// Gebied 4/5: weergave met en zonder JavaScript vergelijken (Chromium, offline).
// Verzoeken naar de vier domeinen worden uit de lokale repo's bediend; al het andere
// externe verkeer (GTM, fonts, YouTube) wordt geblokkeerd, zodat er niets live gaat.
//
// Aanroep:
//   NODE_PATH=$(npm root -g) node audit/scripts/09_render.cjs urls.txt out.json
// urls.txt: een URL per regel (gemaakt door 09_render_prep.py)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const AIBM = path.resolve(__dirname, '..', '..');
const SIS = process.env.AUDIT_SISTERS || path.resolve(AIBM, '..', 'sisters');
const ROOTS = {
  'aibuildermarketplace.com': AIBM,
  'officesoftwaremarketplace.com': path.join(SIS, 'officesoftwaremarketplace'),
  'marketingandsalessoftware.com': path.join(SIS, 'marketingandsalessoftware'),
  'zerotouchsupport.com': path.join(SIS, 'zerotouchsupport'),
};
const TYPES = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.ico': 'image/x-icon', '.txt': 'text/plain', '.xml': 'application/xml' };

function localFile(u) {
  const url = new URL(u);
  const root = ROOTS[url.hostname.replace(/^www\./, '')];
  if (!root) return null;
  let p = decodeURIComponent(url.pathname);
  const cands = p.endsWith('/') ? [p + 'index.html'] : [p, p + '.html', p + '/index.html'];
  for (const c of cands) {
    const f = path.join(root, c);
    if (f.startsWith(root) && fs.existsSync(f) && fs.statSync(f).isFile()) return f;
  }
  return undefined; // eigen domein, maar geen bestand
}

async function snapshot(page) {
  return page.evaluate(() => {
    const q = (s) => Array.from(document.querySelectorAll(s));
    return {
      title: document.title,
      canonical: q('link[rel="canonical"]').map((l) => l.getAttribute('href')),
      robots: q('meta[name="robots"],meta[name="googlebot"]').map((m) => m.getAttribute('name') + '=' + m.getAttribute('content')),
      h1: q('h1').map((h) => h.innerText.trim()).slice(0, 3),
      text: document.body ? document.body.innerText : '',
      links: q('a[href]').length,
      jsonld: q('script[type="application/ld+json"]').length,
    };
  });
}

(async () => {
  const [, , listFile, outFile] = process.argv;
  const urls = fs.readFileSync(listFile, 'utf8').split('\n').map((s) => s.trim()).filter(Boolean);
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
  const mk = async (js) => {
    const ctx = await browser.newContext({ javaScriptEnabled: js, viewport: { width: 412, height: 915 },
      userAgent: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Mobile Safari/537.36 (compatible; audit-render)' });
    await ctx.route('**/*', (route) => {
      const u = route.request().url();
      if (!u.startsWith('http')) return route.continue();
      const f = localFile(u);
      if (f === null) return route.abort();
      if (f === undefined) return route.fulfill({ status: 404, body: 'not found' });
      const ext = path.extname(f).toLowerCase();
      return route.fulfill({ status: 200, body: fs.readFileSync(f), contentType: TYPES[ext] || 'application/octet-stream' });
    });
    return ctx;
  };
  const ctxJs = await mk(true);
  const ctxNo = await mk(false);
  const results = [];
  let i = 0;
  for (const u of urls) {
    i++;
    const rec = { url: u };
    for (const [label, ctx] of [['nojs', ctxNo], ['js', ctxJs]]) {
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', (e) => errors.push(String(e).slice(0, 160)));
      try {
        await page.goto(u, { waitUntil: 'load', timeout: 20000 });
        if (label === 'js') await page.waitForTimeout(600);
        rec[label] = await snapshot(page);
        if (label === 'js') {
          rec.js.errors = errors;
          rec.js.scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        }
      } catch (e) {
        rec[label] = { error: String(e).slice(0, 200) };
      }
      await page.close();
    }
    results.push(rec);
    if (i % 50 === 0) console.error(`${i}/${urls.length}`);
  }
  await browser.close();
  fs.writeFileSync(outFile, JSON.stringify(results));
  console.error('klaar', results.length);
})();
