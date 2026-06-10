#!/usr/bin/env python3
"""Zichtbare taalswitcher op artikelpagina's, opgebouwd uit de bestaande
hreflang-tags (build_hreflang.py is de bron van de clusters). Geen JS:
<details>-dropdown. Idempotent én self-healing: bestaande switcher wordt
elke run opnieuw opgebouwd, dus nieuwe taalvarianten verschijnen vanzelf
en pagina's die uit een cluster vallen raken de switcher weer kwijt.

Gebruik: python3 inject_lang_switcher.py [--apply] [repo_root]
"""
import re
import sys
from pathlib import Path

NATIVE = {
    "en": "English", "nl": "Nederlands", "de": "Deutsch", "fr": "Français",
    "es": "Español", "es-MX": "Español (México)", "pt": "Português",
    "pt-BR": "Português (Brasil)", "it": "Italiano", "pl": "Polski",
    "sv": "Svenska", "da": "Dansk", "no": "Norsk", "fi": "Suomi",
    "ja": "日本語", "ko": "한국어", "zh": "中文", "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia", "th": "ไทย", "tr": "Türkçe", "ru": "Русский",
    "uk": "Українська", "cs": "Čeština", "hu": "Magyar", "ro": "Română",
    "el": "Ελληνικά", "ar": "العربية", "hi": "हिन्दी", "sw": "Kiswahili",
    "ha": "Hausa", "yo": "Yorùbá", "am": "አማርኛ", "zu": "isiZulu",
    "af": "Afrikaans",
}

CSS = (
    '<style id="lang-sw-css">'
    ".lang-switcher{position:relative;display:inline-block;margin-top:14px;font-size:14px}"
    ".lang-switcher summary{cursor:pointer;list-style:none;display:inline-flex;align-items:center;gap:7px;"
    "padding:6px 14px;border:1px solid var(--border);border-radius:20px;color:var(--text2);background:var(--card)}"
    ".lang-switcher summary::-webkit-details-marker{display:none}"
    ".lang-switcher summary:hover,.lang-switcher[open] summary{border-color:var(--accent);color:var(--text)}"
    ".lang-switcher ul{position:absolute;left:0;z-index:50;margin:6px 0 0;padding:8px;list-style:none;"
    "background:var(--card);border:1px solid var(--border);border-radius:12px;max-height:300px;overflow:auto;"
    "min-width:210px;box-shadow:0 8px 24px rgba(0,0,0,.5)}"
    ".lang-switcher li a{display:block;padding:6px 10px;border-radius:8px;color:var(--text2);text-decoration:none;white-space:nowrap}"
    ".lang-switcher li a:hover{background:var(--accent);color:#fff}"
    ".lang-switcher li.cur a{color:var(--text);font-weight:600;opacity:.55;pointer-events:none}"
    "</style>"
)

HREFLANG_RE = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"\s*/?>')
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
OLD_CSS_RE = re.compile(r'<style id="lang-sw-css">.*?</style>\n?', re.S)
OLD_SW_RE = re.compile(r'\n[ \t]*<details class="lang-switcher">.*?</details>', re.S)
HEADER_CLOSE_RE = re.compile(r"\n[ \t]*</header>")
HTML_LANG_RE = re.compile(r'<html[^>]*\blang="([^"]+)"')


def build_switcher(variants, current_href, page_lang):
    cur_name = None
    items = []
    for code, href in variants:
        name = NATIVE.get(code, code)
        is_cur = href.rstrip("/") == current_href.rstrip("/")
        if is_cur:
            cur_name = name
        items.append((name, href, is_cur))
    if cur_name is None:
        cur_name = NATIVE.get(page_lang, page_lang)
    items.sort(key=lambda x: x[0].lower())
    lis = "".join(
        f'<li class="cur"><a>{n} ✓</a></li>' if cur else f'<li><a href="{h}">{n}</a></li>'
        for n, h, cur in items
    )
    return (
        '<details class="lang-switcher"><summary>🌐 '
        f"{cur_name} · {len(items)}</summary><ul>{lis}</ul></details>"
    )


def fix_page(html: str):
    # oude switcher altijd eerst strippen (rebuild = self-healing)
    base = OLD_SW_RE.sub("", OLD_CSS_RE.sub("", html))
    variants = [(c, h) for c, h in HREFLANG_RE.findall(base) if c != "x-default"]
    # dedupe met behoud van volgorde
    seen = set()
    variants = [(c, h) for c, h in variants if not (c in seen or seen.add(c))]
    if len(variants) < 2:
        return (base, "switcher verwijderd (cluster < 2)") if base != html else (None, "geen cluster")
    if not HEADER_CLOSE_RE.search(base) or "</head>" not in base:
        return (base, "geen header — overgeslagen") if base != html else (None, "geen header")
    canonical = CANONICAL_RE.search(base)
    page_lang = (HTML_LANG_RE.search(base) or [None, "en"])[1]
    sw = build_switcher(variants, canonical.group(1) if canonical else "", page_lang)
    out = base.replace("</head>", CSS + "\n</head>", 1)
    out = HEADER_CLOSE_RE.sub(lambda m: "\n  " + sw + m.group(0), out, count=1)
    if out == html:
        return None, "al goed"
    return out, f"switcher met {len(variants)} talen"


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
