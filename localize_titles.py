#!/usr/bin/env python3
"""Lokaliseer <title>, og:title, twitter:title en JSON-LD headline op
niet-Engelse artikelpagina's, afgeleid van de (gelokaliseerde) H1.
Idempotent. Engelse pagina's worden overgeslagen.

Gebruik: python3 localize_titles.py [--apply] [repo_root]
"""
import json
import re
import sys
from pathlib import Path

BRAND = " | AIBuilder Marketplace"
MAX_HEADLINE = 57

H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.S)
TITLE_RE = re.compile(r"<title>.*?</title>", re.S)
OG_TITLE_RE = re.compile(r'(<meta property="og:title" content=")[^"]*(")')
TW_TITLE_RE = re.compile(r'(<meta name="twitter:title" content=")[^"]*(")')
HEADLINE_RE = re.compile(r'("headline":\s*)"((?:[^"\\]|\\.)*)"')
LANG_RE = re.compile(r'<html[^>]*\blang="([^"]+)"')
# leidende emoji/symbolen (vlaggen, pictogrammen) wegstrippen
LEAD_JUNK_RE = re.compile(r"^[\W\s]*?(?=[\w&])", re.UNICODE)


def short_headline(h1_text: str) -> str:
    t = h1_text.strip()
    # leidende/afsluitende emoji en tekens weg, letters/cijfers (alle talen) behouden
    t = LEAD_JUNK_RE.sub("", t)
    t = re.sub(r"[^\w)&%+!?']+$", "", t, flags=re.UNICODE)
    if len(t) <= MAX_HEADLINE:
        return t
    # afkappen op woordgrens; geen afkap op ':' want dan verdwijnen vaak de merknamen
    cut = t[: MAX_HEADLINE + 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    cut = cut.strip().rstrip(",;:–—-")
    # bungelende korte slotwoordjes/getallen weghalen ("... Después de 30" -> "... Después")
    words = cut.split(" ")
    while len(words) > 3 and (words[-1].isdigit() or len(re.sub(r"\W", "", words[-1])) <= 2):
        words.pop()
    return " ".join(words).rstrip(",;:–—-")


def fix_page(html: str):
    lang_m = LANG_RE.search(html)
    if not lang_m or lang_m.group(1).split("-")[0] == "en":
        return None, "en/onbekend"
    h1s = H1_RE.findall(html)
    if not h1s:
        return None, "geen h1"
    headline = short_headline(re.sub(r"<[^>]+>", "", h1s[0]))
    if not headline:
        return None, "lege headline"
    new_title = headline + BRAND
    attr_title = new_title.replace('"', "&quot;")

    out = TITLE_RE.sub(lambda m: f"<title>{new_title}</title>", html, count=1)
    out = OG_TITLE_RE.sub(lambda m: m.group(1) + attr_title + m.group(2), out, count=1)
    out = TW_TITLE_RE.sub(lambda m: m.group(1) + attr_title + m.group(2), out, count=1)
    # JSON-LD headline: zonder brand-suffix, JSON-veilig escapen
    json_headline = json.dumps(headline, ensure_ascii=False)
    out = HEADLINE_RE.sub(lambda m: m.group(1) + json_headline, out, count=1)
    if out == html:
        return None, "al goed"
    return out, headline


def main():
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]
    root = Path(args[0]) if args else Path(".")
    pages = sorted((root / "b2b").glob("*/index.html"))
    fixed = skipped = 0
    for page in pages:
        html = page.read_text(encoding="utf-8")
        new_html, info = fix_page(html)
        if new_html is None:
            skipped += 1
            continue
        fixed += 1
        print(f"{'FIX ' if apply else 'DRY '} {page.parent.name}: {info}")
        if apply:
            page.write_text(new_html, encoding="utf-8")
    print(f"\n{'Toegepast' if apply else 'Dry-run'}: {fixed} aan te passen, {skipped} overgeslagen, {len(pages)} totaal")


if __name__ == "__main__":
    main()
