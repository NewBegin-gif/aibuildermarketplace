#!/usr/bin/env python3
"""Fix 2xH1 op artikelpagina's: header-h1 krijgt de gelokaliseerde body-titel,
body-h1 wordt verwijderd, extra h1's worden h2. Idempotent.

Gebruik: python3 fix_double_h1.py [--apply] [repo_root]
Zonder --apply: dry-run met rapportage.
"""
import re
import sys
from pathlib import Path

H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.S)
TAG_RE = re.compile(r"<[^>]+>")


def fix_page(html: str):
    """Geeft (nieuwe_html, omschrijving) of (None, reden_overgeslagen)."""
    matches = list(H1_RE.finditer(html))
    if len(matches) < 2:
        return None, f"ok ({len(matches)} h1)"

    body_start = html.find('<article class="article-body"')
    header_start = html.find('<header class="article-header"')
    if body_start == -1 or header_start == -1:
        # fallback: eerste h1 behouden, rest naar h2
        out = html[: matches[0].end()]
        rest = html[matches[0].end():]
        rest = rest.replace("<h1", "<h2").replace("</h1>", "</h2>")
        return out + rest, "fallback: extra h1 -> h2"

    header_h1 = next((m for m in matches if m.start() > header_start and m.start() < body_start), None)
    body_h1s = [m for m in matches if m.start() > body_start]
    if header_h1 is None or not body_h1s:
        out = html[: matches[0].end()]
        rest = html[matches[0].end():]
        rest = rest.replace("<h1", "<h2").replace("</h1>", "</h2>")
        return out + rest, "fallback: extra h1 -> h2"

    # gelokaliseerde titel uit de eerste body-h1, zonder inline tags/styles
    new_title = TAG_RE.sub("", body_h1s[0].group(1)).strip()

    parts = []
    # header-h1 vervangen door schone h1 met de volledige titel
    parts.append(html[: header_h1.start()])
    parts.append(f"<h1>{new_title}</h1>")
    pos = header_h1.end()
    # eerste body-h1 (incl. omliggende newlines niet nodig) verwijderen
    first = body_h1s[0]
    parts.append(html[pos: first.start()])
    pos = first.end()
    # eventuele extra body-h1's demoten naar h2
    for extra in body_h1s[1:]:
        parts.append(html[pos: extra.start()])
        inner = extra.group(1)
        parts.append(f"<h2>{inner}</h2>")
        pos = extra.end()
    parts.append(html[pos:])
    new_html = "".join(parts)
    desc = f"h1 -> '{new_title[:60]}'"
    if len(body_h1s) > 1:
        desc += f" (+{len(body_h1s) - 1} h1->h2)"
    return new_html, desc


def main():
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]
    root = Path(args[0]) if args else Path(".")
    pages = sorted((root / "b2b").glob("*/index.html"))
    fixed = skipped = 0
    for page in pages:
        html = page.read_text(encoding="utf-8")
        new_html, desc = fix_page(html)
        if new_html is None:
            skipped += 1
            continue
        fixed += 1
        print(f"{'FIX ' if apply else 'DRY '} {page.parent.name}: {desc}")
        if apply:
            page.write_text(new_html, encoding="utf-8")
    print(f"\n{'Toegepast' if apply else 'Dry-run'}: {fixed} pagina's te fixen, {skipped} al ok, {len(pages)} totaal")


if __name__ == "__main__":
    main()
