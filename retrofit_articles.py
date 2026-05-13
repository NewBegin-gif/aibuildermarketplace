"""
retrofit_articles.py — Re-wrap alle bestaande b2b artikelen met review_template.py V2.
─────────────────────────────────────────────────────────────────────────────
Wat het doet:
1. Loopt door elke /b2b/*/index.html
2. Extraheert: title, brand1, slug, schema_json, en de pure body content
3. Strip oude CTA blokken (Ready to try, Read more B2B Insights, More AI Tools)
4. Roept build_article_html_v2() aan met de schone content
5. Schrijft het nieuwe HTML terug

Gebruik (lokaal):
    python3 retrofit_articles.py /pad/naar/aibuildermarketplace-main/b2b

Gebruik (VPS):
    python3 retrofit_articles.py /root/felix_hq/repos/aibuildermarketplace/b2b

Flags:
    --dry-run    Toon wat er zou gebeuren, schrijf niets weg
    --limit N    Verwerk maximaal N artikelen (voor testen)
    --only SLUG  Verwerk alleen een specifieke slug
"""
import os, sys, re, json, argparse, traceback
from pathlib import Path

# Importeer template uit zelfde directory
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from review_template import build_article_html_v2, AFFILIATE


# ─────────────────────────────────────────────────────────────────────────
# EXTRACTORS
# ─────────────────────────────────────────────────────────────────────────
def extract_title(html):
    """Probeer titel uit <h1> in article-header, anders uit <title>."""
    # Eerst: <h1> binnen article-header (meest accuraat)
    m = re.search(
        r'<header[^>]*class="[^"]*article-header[^"]*"[^>]*>.*?<h1[^>]*>(.*?)</h1>',
        html, re.IGNORECASE | re.DOTALL
    )
    if not m:
        # Fallback: eerste <h1>
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        return text
    # Laatste fallback: <title>
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        # Strip site suffix
        for sep in [" | AIBuilder", " - AIBuilder"]:
            if sep in text:
                text = text.split(sep)[0]
        text = re.sub(r"\s+2026\s*$", "", text)
        return text.strip()
    return "Review"


def _norm(s):
    """Normalize: lowercase, strip non-alphanumeric."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def extract_brand(html, slug):
    """Probeer brand uit <span class='tag'>, anders uit slug."""
    candidates = []
    m = re.search(r'<span[^>]*class="[^"]*tag[^"]*"[^>]*>(.*?)</span>', html, re.IGNORECASE | re.DOTALL)
    if m:
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if text:
            candidates.append(text)
    # Slug fallback (na "best-" prefix)
    s = slug.lower()
    if s.startswith("best-"):
        s = s[5:]
    candidates.append(s)

    # Match candidates (normalized) tegen AFFILIATE keys
    aff_norm = {_norm(k): k for k in AFFILIATE.keys()}
    for cand in candidates:
        cn = _norm(cand)
        # Exact match
        if cn in aff_norm:
            return aff_norm[cn]
        # Prefix match (slug start with brand)
        for an, real in aff_norm.items():
            if cn.startswith(an) and len(an) >= 4:
                return real
    # Geef de raw tag terug als die er was
    if m and text:
        return text
    return "AI Tool"


def extract_body(html):
    """Pak de inhoud binnen <article class='article-body'>...</article>."""
    m = re.search(
        r'<article[^>]*class="[^"]*article-body[^"]*"[^>]*>(.*?)</article>',
        html, re.IGNORECASE | re.DOTALL
    )
    if m:
        return m.group(1)
    return None


def extract_schema(html):
    """Pak de eerste Article/Review schema script."""
    matches = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL
    )
    for raw in matches:
        try:
            data = json.loads(raw.strip())
            if isinstance(data, dict) and data.get("@type") in ("Article", "Review", "NewsArticle"):
                return f"<script type='application/ld+json'>\n{json.dumps(data, indent=2)}\n</script>"
        except Exception:
            continue
    return ""


# ─────────────────────────────────────────────────────────────────────────
# CONTENT CLEANER — verwijder oude wrapper-elementen uit body
# ─────────────────────────────────────────────────────────────────────────
def strip_old_wrappers(body):
    """Verwijder alle oude main_cta / mid_cta / footer / internal_links blokken
    die per ongeluk binnen <article class='article-body'> staan."""
    if not body:
        return body

    # 1) "Ready to try ..." CTA blok
    body = re.sub(
        r'<div\s+style=["\'][^"\']*(?:margin:40px 0|background:linear-gradient[^"\']*0d1117|background:linear-gradient[^"\']*0a0e17)[^"\']*["\'][^>]*>\s*<h2[^>]*>\s*Ready to try[^<]*</h2>.*?</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Algemenere fallback voor Ready to try
    body = re.sub(
        r'<div[^>]*>\s*<h2[^>]*>\s*Ready to try[^<]*</h2>.*?</div>\s*</div>?',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 2) Mid CTA: "Try X risk-free" of "Start your free trial"
    body = re.sub(
        r'<div\s+style=["\'][^"\']*border-left:4px solid[^"\']*["\'][^>]*>\s*<p[^>]*>\s*<strong>\s*Try [^<]+ risk-free:.*?</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 3) Internal links "Read more B2B Insights"
    body = re.sub(
        r'<div\s+style=["\'][^"\']*border-top:1px solid #eee[^"\']*["\'][^>]*>\s*<h4[^>]*>\s*Read more[^<]*</h4>.*?</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Variant met B2B Insights tekst zonder #eee style
    body = re.sub(
        r'<div[^>]*>\s*<h4[^>]*>\s*Read more B2B Insights[^<]*</h4>.*?</ul>\s*</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 4) "More AI Tools for Founders" blok
    body = re.sub(
        r'<div\s+style=["\'][^"\']*background:#161b22[^"\']*["\'][^>]*>\s*<h3[^>]*>\s*More AI Tools[^<]*</h3>.*?</ul>\s*</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    body = re.sub(
        r'<div[^>]*>\s*<h3[^>]*>\s*More AI Tools for Founders[^<]*</h3>.*?</ul>\s*</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    body = re.sub(
        r'<div[^>]*background:#111827[^>]*>\s*<h3[^>]*>\s*More AI Tools[^<]*</h3>.*?</ul>\s*</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 5) NIEUWE-TEMPLATE wrappers — idempotency: verwijder als die er al staan
    # mid-cta blok uit V2
    body = re.sub(
        r'<div\s+class="mid-cta"[^>]*>.*?</div>\s*</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    body = re.sub(
        r'<div\s+class="mid-cta"[^>]*>.*?</div>',
        '',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # 6) Trim whitespace
    body = body.strip()
    return body


# ─────────────────────────────────────────────────────────────────────────
# MAIN RETROFIT
# ─────────────────────────────────────────────────────────────────────────
def retrofit_one(folder_path: Path, dry_run=False, verbose=False):
    slug = folder_path.name
    index_path = folder_path / "index.html"
    if not index_path.is_file():
        return None, "geen index.html"

    try:
        html = index_path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"lees-fout: {e}"

    title = extract_title(html)
    brand1 = extract_brand(html, slug)
    body = extract_body(html)
    schema_json = extract_schema(html)

    if not body:
        return None, "geen <article class='article-body'> gevonden"

    clean_body = strip_old_wrappers(body)

    if verbose:
        print(f"  title='{title}' brand='{brand1}' body_len={len(clean_body)}")

    # Genereer nieuwe HTML
    try:
        new_html = build_article_html_v2(
            title=title,
            content=clean_body,
            brand1=brand1,
            slug=slug,
            schema_json=schema_json,
            internal_links_html="",  # nieuwe template heeft eigen "more tools" sectie
        )
    except Exception as e:
        return None, f"template-bouw fout: {e}\n{traceback.format_exc()}"

    if dry_run:
        return {"slug": slug, "title": title, "brand": brand1, "size": len(new_html)}, None

    try:
        index_path.write_text(new_html, encoding="utf-8")
    except Exception as e:
        return None, f"schrijf-fout: {e}"

    return {"slug": slug, "title": title, "brand": brand1, "size": len(new_html)}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("b2b_dir", help="Pad naar /b2b/ directory")
    ap.add_argument("--dry-run", action="store_true", help="Test zonder schrijven")
    ap.add_argument("--limit", type=int, default=0, help="Max aantal te verwerken")
    ap.add_argument("--only", default="", help="Alleen deze slug verwerken")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    b2b = Path(args.b2b_dir).resolve()
    if not b2b.is_dir():
        print(f"❌ {b2b} is geen directory")
        sys.exit(1)

    folders = sorted([f for f in b2b.iterdir() if f.is_dir() and f.name != ".git"])
    if args.only:
        folders = [f for f in folders if f.name == args.only]
    if args.limit:
        folders = folders[: args.limit]

    print(f"🚀 Retrofit start — {len(folders)} artikelen, dry_run={args.dry_run}")
    print(f"📁 {b2b}\n")

    ok = 0
    skipped = 0
    errors = []

    for i, f in enumerate(folders, 1):
        result, err = retrofit_one(f, dry_run=args.dry_run, verbose=args.verbose)
        if err:
            errors.append((f.name, err))
            print(f"  [{i}/{len(folders)}] ⚠️  {f.name} — {err}")
            skipped += 1
        else:
            ok += 1
            if i % 25 == 0 or args.verbose:
                print(f"  [{i}/{len(folders)}] ✅ {result['slug']} — {result['brand']}")

    print(f"\n{'='*60}")
    print(f"✅ Gereed: {ok}  ⚠️  Overgeslagen: {skipped}")
    if errors and args.verbose:
        print("\nFouten:")
        for slug, err in errors[:20]:
            print(f"  • {slug}: {err}")
    if args.dry_run:
        print("\n⚠️  DRY-RUN: geen bestanden geschreven.")


if __name__ == "__main__":
    main()
