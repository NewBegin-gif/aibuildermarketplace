// Gebied 6: toegankelijkheid-steekproef met axe-core (contrast, labels, namen, alt, lang, viewport).
// Offline zoals 09_render.cjs: de vier domeinen komen uit de lokale repo's, de rest wordt geblokkeerd
// (dus ook Google Fonts: contrast wordt met de terugvalletters gemeten).
//
// Aanroep:
//   AXE=/pad/naar/axe.min.js NODE_PATH=$(npm root -g) node audit/scripts/11_axe.cjs out.json
// axe-core: `npm install axe-core@4.10.3` in een losse map; geef het pad mee in $AXE.
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
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' };
const SAMPLE = [
  'https://aibuildermarketplace.com/', 'https://aibuildermarketplace.com/b2b/1password-review/',
  'https://aibuildermarketplace.com/b2b/', 'https://aibuildermarketplace.com/atlas/',
  'https://aibuildermarketplace.com/tools/renewal-check/', 'https://aibuildermarketplace.com/roi-calculator/',
  'https://aibuildermarketplace.com/research/saas-pricing-transparency-2026/',
  'https://officesoftwaremarketplace.com/', 'https://officesoftwaremarketplace.com/adp-review.html',
  'https://officesoftwaremarketplace.com/software.html', 'https://officesoftwaremarketplace.com/best-business-finance.html',
  'https://marketingandsalessoftware.com/', 'https://marketingandsalessoftware.com/beehiiv-review.html',
  'https://marketingandsalessoftware.com/atlas.html',
  'https://zerotouchsupport.com/', 'https://zerotouchsupport.com/aircall-review.html',
  'https://zerotouchsupport.com/best-business-phone-systems.html',
];
const RULES = ['color-contrast', 'label', 'button-name', 'link-name', 'image-alt', 'html-has-lang', 'meta-viewport',
  'document-title', 'select-name', 'input-button-name', 'frame-title', 'heading-order', 'duplicate-id-aria'];

function localFile(u) {
  const url = new URL(u);
  const root = ROOTS[url.hostname.replace(/^www\./, '')];
  if (!root) return null;
  const p = decodeURIComponent(url.pathname);
  const cands = p.endsWith('/') ? [p + 'index.html'] : [p, p + '.html', p + '/index.html'];
  for (const c of cands) {
    const f = path.join(root, c);
    if (f.startsWith(root) && fs.existsSync(f) && fs.statSync(f).isFile()) return f;
  }
  return undefined;
}

(async () => {
  const outFile = process.argv[2];
  const axe = fs.readFileSync(process.env.AXE, 'utf8');
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
  const ctx = await browser.newContext({ viewport: { width: 412, height: 915 } });
  await ctx.route('**/*', (route) => {
    const u = route.request().url();
    if (!u.startsWith('http')) return route.continue();
    const f = localFile(u);
    if (f === null) return route.abort();
    if (f === undefined) return route.fulfill({ status: 404, body: 'not found' });
    return route.fulfill({ status: 200, body: fs.readFileSync(f), contentType: TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' });
  });
  const results = [];
  for (const u of SAMPLE) {
    const page = await ctx.newPage();
    try {
      await page.goto(u, { waitUntil: 'load', timeout: 20000 });
      await page.waitForTimeout(500);
      await page.addScriptTag({ content: axe });
      const r = await page.evaluate(async (rules) => {
        const res = await axe.run(document, { runOnly: { type: 'rule', values: rules } });
        return res.violations.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length,
          voorbeelden: v.nodes.slice(0, 3).map((n) => ({ target: n.target.join(' '), html: n.html.slice(0, 160),
            info: (n.any[0] && n.any[0].message || '').slice(0, 160) })) }));
      }, RULES);
      results.push({ url: u, violations: r });
      console.error(u, r.map((v) => `${v.id}:${v.n}`).join(' '));
    } catch (e) {
      results.push({ url: u, error: String(e).slice(0, 200) });
    }
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(outFile, JSON.stringify(results, null, 1));
})();
