#!/usr/bin/env python3
"""Backfill GA4 + conversion.js op artikelpagina's die de tag missen.
Idempotent: pagina's met googletagmanager worden overgeslagen.

Gebruik: python3 backfill_ga4.py [--apply] [repo_root]
"""
import sys
from pathlib import Path

SNIPPET = """
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-CW1KZ258ZV"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-CW1KZ258ZV');
  </script>
  <script defer src="/assets/conversion.js?v=1"></script>"""

ANCHOR = '<meta charset="UTF-8">'


def main():
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]
    root = Path(args[0]) if args else Path(".")
    pages = sorted((root / "b2b").glob("*/index.html"))
    fixed = skipped = 0
    for page in pages:
        html = page.read_text(encoding="utf-8")
        if "googletagmanager" in html or ANCHOR not in html:
            skipped += 1
            continue
        fixed += 1
        print(f"{'FIX ' if apply else 'DRY '} {page.parent.name}")
        if apply:
            page.write_text(html.replace(ANCHOR, ANCHOR + SNIPPET, 1), encoding="utf-8")
    print(f"\n{'Toegepast' if apply else 'Dry-run'}: {fixed} aan te passen, {skipped} overgeslagen, {len(pages)} totaal")


if __name__ == "__main__":
    main()
