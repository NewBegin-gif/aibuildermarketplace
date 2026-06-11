#!/usr/bin/env python3
"""Verdict-box boven de vouw op AIBM /b2b/-reviewpagina's: rating (uit de
Review-JSON-LD die al op de pagina staat), prijs (uit de meta description),
merk-CTA en — voor hero-merken — een link naar Daans hands-on review.

Strikt veilig:
  - Alleen data die al op de pagina staat; niets verzonnen.
  - CTA alleen als er een sponsored link is die bij het MERK van de pagina hoort
    (eerste-link-pakken is fout: op sommige pagina's is dat een ander merk).
  - Pagina's zonder rating, merk-match of article-header worden overgeslagen.
  - Hero-pagina's zelf overgeslagen (hebben eigen design).
  - Rebuild-based (zelfde patroon als de taalswitcher): bestaande box wordt elke
    run opnieuw opgebouwd -> self-healing in de bestaande VPS-cron.

Gebruik: python3 inject_verdict_box.py [--apply] [repo_root]
"""
import json
import re
import sys
from pathlib import Path

HEROES = {
    "bitvavo": "/b2b/bitvavo-trading-bot/",
    "replit": "/b2b/replit-trading-bot/",
    "hostinger": "/b2b/hostinger-vps-review/",
    "turbotic": "/b2b/turbotic-ai-review/",
    "calilio": "/b2b/calilio-review/",
    "cometchat": "/b2b/cometchat-review/",
    "krispcall": "/b2b/krispcall-review/",
    "reply": "/b2b/reply-io-review/",
    "typewise": "/b2b/typewise-review/",
    "vida": "/b2b/vida-ai-review/",
    "aisq": "/b2b/aisq-review/",
    "browseai": "/b2b/browse-ai-review/",
    "clickup": "/b2b/clickup-review/",
    "gamma": "/b2b/gamma-review/",
    "idrive": "/b2b/idrive-review/",
    "lindy": "/b2b/lindy-review/",
    "proton": "/b2b/proton-review/",
    "quillbot": "/b2b/quillbot-review/",
    "reclaim": "/b2b/reclaim-ai-review/",
    "sanebox": "/b2b/sanebox-review/",
    "trainual": "/b2b/trainual-review/",
    "vistasocial": "/b2b/vista-social-review/",
    "consensus": "/b2b/consensus-review/",
    "mindstudio": "/b2b/mindstudio-review/",
    "runpod": "/b2b/runpod-review/",
    "processstreet": "/b2b/process-street-review/",
    "quo": "/b2b/quo-review/",
    "flocksy": "/b2b/flocksy-review/",
    "brightdata": "/b2b/bright-data-review/",
}
HERO_SLUGS = {"bitvavo-trading-bot", "replit-trading-bot", "hostinger-vps-review", "turbotic-ai-review",
              "calilio-review", "cometchat-review", "krispcall-review", "reply-io-review", "typewise-review", "vida-ai-review", "aisq-review", "browse-ai-review", "clickup-review", "gamma-review", "idrive-review", "lindy-review", "proton-review", "quillbot-review", "reclaim-ai-review", "sanebox-review", "trainual-review", "vista-social-review", "consensus-review", "mindstudio-review", "runpod-review",
              "process-street-review", "quo-review", "flocksy-review", "bright-data-review"}

OLD_BOX_RE = re.compile(r'\n[ \t]*<div class="verdict-box".*?</div>', re.S)
H1_CLOSE_RE = re.compile(r"</h1>")
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
TAG_RE = re.compile(r'<span class="tag">([^<]+)</span>')
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"')
SPONSORED_RE = re.compile(r'<a href="(https://[^"]+)"[^>]*rel="[^"]*sponsored')


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def page_data(html):
    """(brand, rating, price, aff_url) of None als de pagina niet geschikt is."""
    m = TAG_RE.search(html)
    if not m:
        return None
    brand = m.group(1).strip()
    rating = None
    for ld in LD_RE.findall(html):
        try:
            d = json.loads(ld)
        except Exception:
            continue
        if d.get("@type") == "Review":
            rating = (d.get("reviewRating") or {}).get("ratingValue")
    if not rating:
        return None
    nb = norm(brand)
    aff = None
    for url in SPONSORED_RE.findall(html):
        host = re.sub(r"^https://", "", url).split("/")[0]
        if nb and nb in norm(host):
            aff = url
            break
    if not aff:
        return None
    price = None
    dm = DESC_RE.search(html)
    if dm:
        pm = re.search(r"★[^,]{0,30},\s*([^.]{2,24})\.", dm.group(1))
        if pm and "★" not in pm.group(1):
            cand = pm.group(1).strip()
            if len(cand) >= 4 and re.search(r"[$€£]|/mo|/yr|free|varies|custom|demo|trial", cand, re.I):
                price = cand
    return brand, rating, price, aff


def build_box(brand, rating, price, aff):
    price_html = (f'<span style="color:var(--text2)">{price}</span>' if price else "")
    nb = norm(brand)
    hero = next((u for k, u in HEROES.items() if nb.startswith(k)), None)
    hero_html = (f'<a href="{hero}" style="color:var(--text2);font-size:.85rem;text-decoration:underline">'
                 f"My hands-on review →</a>" if hero else "")
    return (
        '<div class="verdict-box" style="display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;'
        'margin:18px 0 4px;padding:13px 18px;background:var(--card);border:1px solid var(--border);'
        'border-left:4px solid var(--accent);border-radius:12px;font-size:.92rem">'
        f'<span style="color:var(--text);font-weight:700">★ {rating}</span>'
        f"{price_html}"
        f'<a href="{aff}" rel="sponsored noopener" target="_blank" '
        'style="background:var(--accent);color:#fff;padding:9px 18px;border-radius:8px;'
        f'font-weight:600;text-decoration:none">Visit {brand} →</a>'
        f"{hero_html}"
        "</div>"
    )


def fix_page(html, slug):
    base = OLD_BOX_RE.sub("", html)
    if slug in HERO_SLUGS:
        return (base, "hero — box verwijderd") if base != html else (None, "hero overgeslagen")
    data = page_data(base)
    if data is None:
        return (base, "geen merk-match — box verwijderd") if base != html else (None, "geen data/merk-match")
    if "</h1>" not in base or "</header>" not in base:
        return (None, "geen header/h1")
    box = build_box(*data)
    out = H1_CLOSE_RE.sub(lambda m: m.group(0) + "\n  " + box, base, count=1)
    if out == html:
        return None, "al goed"
    return out, f"box: ★{data[1]} {data[2] or ''} CTA={data[0]}"


def main():
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]
    root = Path(args[0]) if args else Path(".")
    pages = sorted((root / "b2b").glob("*/index.html"))
    fixed = skipped = 0
    for page in pages:
        html = page.read_text(encoding="utf-8")
        out, info = fix_page(html, page.parent.name)
        if out is None:
            skipped += 1
            continue
        fixed += 1
        print(f"{'FIX ' if apply else 'DRY '} {page.parent.name}: {info}")
        if apply:
            page.write_text(out, encoding="utf-8")
    print(f"\n{'Toegepast' if apply else 'Dry-run'}: {fixed} aan te passen, {skipped} overgeslagen, {len(pages)} totaal")


if __name__ == "__main__":
    main()
