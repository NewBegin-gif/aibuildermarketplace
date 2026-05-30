#!/usr/bin/env python3
"""inject_author.py — bulk-insert author identity (Daan) into every article page."""
import argparse, datetime, re, sys
from pathlib import Path

REPO_DEFAULT = "/root/felix_hq/repos/aibuildermarketplace"
MARKER = "<!-- author-box-v1 -->"
CSS_MARKER = "/* author-box-css-v1 */"

AUTHOR_CSS = """
    /* author-box-css-v1 */
    .author-box{display:flex;align-items:center;gap:14px;background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:10px;padding:14px 18px;margin:0 0 24px}
    .author-box img{width:56px;height:56px;border-radius:50%;object-fit:cover;flex-shrink:0;border:2px solid var(--accent)}
    .author-box .ab-text{font-size:.85rem;color:var(--text2);line-height:1.5;min-width:0}
    .author-box .ab-name{color:var(--text);font-weight:700}
    .author-box .ab-name a{color:var(--text)}
    .author-box .ab-meta{color:var(--muted);font-size:.78rem;margin-top:2px}
    .author-box .ab-meta a{color:var(--text2)}
    @media(max-width:640px){.author-box{padding:12px 14px}.author-box img{width:48px;height:48px}}
"""

L10N = {
    "en": {"by": "By",      "updated": "Last updated", "about": "About Daan",         "tag": "Ex-banker (23y) \u00b7 AI builder \u00b7 Writing from Ho Chi Minh City"},
    "fr": {"by": "Par",     "updated": "Mis \u00e0 jour", "about": "\u00c0 propos de Daan", "tag": "Ex-banquier (23 ans) \u00b7 AI builder \u00b7 \u00c9crit depuis H\u00f4-Chi-Minh-Ville"},
    "de": {"by": "Von",     "updated": "Aktualisiert", "about": "\u00dcber Daan",       "tag": "Ex-Banker (23 J.) \u00b7 AI-Builder \u00b7 Schreibt aus Ho-Chi-Minh-Stadt"},
    "es": {"by": "Por",     "updated": "Actualizado",  "about": "Sobre Daan",         "tag": "Ex-banquero (23 a\u00f1os) \u00b7 AI builder \u00b7 Escribiendo desde Ciudad Ho Chi Minh"},
    "it": {"by": "Di",      "updated": "Aggiornato",   "about": "Su Daan",            "tag": "Ex-banchiere (23 anni) \u00b7 AI builder \u00b7 Scrivo da Ho Chi Minh"},
    "pt": {"by": "Por",     "updated": "Atualizado",   "about": "Sobre Daan",         "tag": "Ex-banc\u00e1rio (23 anos) \u00b7 AI builder \u00b7 Escrevendo de Ho Chi Minh"},
    "nl": {"by": "Door",    "updated": "Bijgewerkt",   "about": "Over Daan",          "tag": "Ex-bankier (23 jr) \u00b7 AI builder \u00b7 Schrijft vanuit Ho Chi Minh City"},
    "pl": {"by": "Autor:",  "updated": "Aktualizacja", "about": "O Daanie",           "tag": "By\u0142y bankier (23 lata) \u00b7 AI builder \u00b7 Pisze z Ho Chi Minh"},
    "sv": {"by": "Av",      "updated": "Uppdaterad",   "about": "Om Daan",            "tag": "F.d. bankman (23 \u00e5r) \u00b7 AI builder \u00b7 Skriver fr\u00e5n Ho Chi Minh-staden"},
    "da": {"by": "Af",      "updated": "Opdateret",    "about": "Om Daan",            "tag": "Tidl. bankmand (23 \u00e5r) \u00b7 AI builder \u00b7 Skriver fra Ho Chi Minh City"},
    "no": {"by": "Av",      "updated": "Oppdatert",    "about": "Om Daan",            "tag": "Tidl. bankmann (23 \u00e5r) \u00b7 AI builder \u00b7 Skriver fra Ho Chi Minh"},
    "ja": {"by": "\u8457\u8005",  "updated": "\u6700\u7d42\u66f4\u65b0", "about": "Daan\u306b\u3064\u3044\u3066", "tag": "\u5143\u9280\u884c\u54e1(23\u5e74)\u30fbAI\u30d3\u30eb\u30c0\u30fc\u30fb\u30db\u30fc\u30c1\u30df\u30f3\u5e02\u304b\u3089"},
    "tr": {"by": "Yazar:",  "updated": "G\u00fcncellendi", "about": "Daan Hakk\u0131nda", "tag": "Eski bankac\u0131 (23 y\u0131l) \u00b7 AI builder \u00b7 Ho Chi Minh'den yaz\u0131yor"},
    "id": {"by": "Oleh",    "updated": "Diperbarui",   "about": "Tentang Daan",       "tag": "Mantan bankir (23 thn) \u00b7 AI builder \u00b7 Menulis dari Kota Ho Chi Minh"},
    "vi": {"by": "B\u1edfi",       "updated": "C\u1eadp nh\u1eadt", "about": "V\u1ec1 Daan", "tag": "C\u1ef1u nh\u00e2n vi\u00ean ng\u00e2n h\u00e0ng (23 n\u0103m) \u00b7 AI builder \u00b7 Vi\u1ebft t\u1eeb TP. H\u1ed3 Ch\u00ed Minh"},
    "uk": {"by": "\u0410\u0432\u0442\u043e\u0440:", "updated": "\u041e\u043d\u043e\u0432\u043b\u0435\u043d\u043e", "about": "\u041f\u0440\u043e Daan", "tag": "\u041a\u043e\u043b\u0438\u0448\u043d\u0456\u0439 \u0431\u0430\u043d\u043a\u0456\u0440 (23 \u0440\u043e\u043a\u0438) \u00b7 AI builder \u00b7 \u041f\u0438\u0448\u0435 \u0437 \u0425\u043e\u0448\u0438\u043c\u0456\u043d\u0430"},
}

def get_lang(html_text):
    m = re.search(r'<html\s+lang="([^"]+)"', html_text)
    if not m: return "en"
    base = m.group(1).lower().split("-")[0]
    return base if base in L10N else "en"

def build_author_html(lang_key, last_updated):
    s = L10N.get(lang_key, L10N["en"])
    return ('\n      <div class="author-box" role="note">\n'
            f'        {MARKER}\n'
            '        <img src="/about/daan.jpg" alt="Daan" width="56" height="56" loading="lazy">\n'
            '        <div class="ab-text">\n'
            f'          <div class="ab-name">{s["by"]} <a href="/about/">Daan</a></div>\n'
            f'          <div>{s["tag"]}</div>\n'
            f'          <div class="ab-meta">{s["updated"]}: <time>{last_updated}</time> \u00b7 <a href="/about/">{s["about"]} \u2192</a></div>\n'
            '        </div>\n'
            '      </div>\n')

def patch_one(path, dry):
    text = path.read_text(encoding="utf-8")
    if MARKER in text: return False, "already-injected"
    lang = get_lang(text)
    m = re.search(r'<meta\s+property="article:published_time"\s+content="([^"]+)"', text)
    last_updated = m.group(1) if m else datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
    new_text, n_html = re.subn(r"(</header>)", r"\1" + build_author_html(lang, last_updated), text, count=1)
    if n_html == 0: return False, "no </header> found"
    if CSS_MARKER not in new_text:
        new_text, n_css = re.subn(r"(</style>)", AUTHOR_CSS + r"\1", new_text, count=1)
        if n_css == 0: return False, "no </style> found"
    person_author = '"author": {"@type": "Person", "name": "Daan", "url": "https://aibuildermarketplace.com/about/"}'
    new_text = re.sub(r'"author":\s*\{\s*"@type":\s*"Organization",\s*"name":\s*"AIBuilder Marketplace"\s*\}', person_author, new_text, flags=re.DOTALL)
    if not dry: path.write_text(new_text, encoding="utf-8")
    return True, f"patched ({lang}, updated={last_updated})"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo); b2b = repo / "b2b"
    if not b2b.exists(): print(f"ERROR: b2b dir not found at {b2b}", file=sys.stderr); return 1
    files = sorted(b2b.glob("*/index.html"))
    if not args.quiet: print(f"Found {len(files)} articles\nMode: {'APPLY' if args.apply else 'DRY-RUN'}\n")
    patched = already = failed = 0
    for p in files:
        changed, reason = patch_one(p, dry=not args.apply)
        if changed:
            patched += 1
            if not args.quiet: print(f"  + {p.parent.name}: {reason}")
        elif reason == "already-injected": already += 1
        else: failed += 1; print(f"  ! {p.parent.name}: {reason}", file=sys.stderr)
    print(f"\nSummary: {patched} {'patched' if args.apply else 'would-patch'}, {already} already-done, {failed} failed")
    return 0 if failed == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
