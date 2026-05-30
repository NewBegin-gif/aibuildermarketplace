#!/usr/bin/env python3
"""
add_languages.py — voegt 17 nieuwe talen toe aan de B2B-pipeline.

Nieuwe talen (schone ISO-codes als slug-suffix, geen botsing met legacy du/ge/sp/po):
  zh ko hi ar th ru cs fi el hu ro sw ha yo am af zu

Raakt 3 files (allemaal idempotent + met backup + syntaxcheck):
  1) b2b/index.html        -> 17 filterknoppen toevoegen na de 'vi'-knop
  2) review_template.py     -> LANG_MAP_SUFFIX uitbreiden + LABELS-subdicts toevoegen
                               (Engelse fallback voor UI-labels, VERTAALDE meta_description)
  3) generate_article.py    -> lang_map uitbreiden + LANG_DESCRIPTIONS uitbreiden

Aanpak voor labels: zelfde keuze als de vorige uitbreiding (patch_article_generator.py)
— UI-strings krijgen Engelse fallback, alleen meta_description/lang_description zijn
vertaald (hoogste SEO-waarde). Compare-templates (generate_compare.py) en het
daadwerkelijk GENEREREN van artikelen zijn aparte vervolgstappen.

DRY-RUN is standaard: het script schrijft NIETS tenzij je --apply meegeeft.

Gebruik op de VPS:
    cd /root/felix_hq/repos/aibuildermarketplace
    python3 add_languages.py            # dry-run: laat zien wat het zou doen
    python3 add_languages.py --apply    # echt toepassen (met backups)
    python3 add_languages.py --apply /ander/pad   # andere repo-root
"""

from __future__ import annotations
import os, re, sys, shutil, datetime
from pathlib import Path

# ─── Configuratie ─────────────────────────────────────────────────────────
ROOT = Path("/root/felix_hq/repos/aibuildermarketplace")

# (english_name, code/suffix, iso, flag, native, is_EU)  is_EU=True -> Bitvavo toegestaan
NEW_LANGS = [
    ("Chinese",    "zh", "zh", "🇨🇳", "中文",        False),
    ("Korean",     "ko", "ko", "🇰🇷", "한국어",       False),
    ("Hindi",      "hi", "hi", "🇮🇳", "हिन्दी",       False),
    ("Arabic",     "ar", "ar", "🇸🇦", "العربية",      False),  # RTL — polish later
    ("Thai",       "th", "th", "🇹🇭", "ไทย",         False),
    ("Russian",    "ru", "ru", "🇷🇺", "Русский",      False),
    ("Czech",      "cs", "cs", "🇨🇿", "Čeština",      True),
    ("Finnish",    "fi", "fi", "🇫🇮", "Suomi",        True),
    ("Greek",      "el", "el", "🇬🇷", "Ελληνικά",     True),
    ("Hungarian",  "hu", "hu", "🇭🇺", "Magyar",       True),
    ("Romanian",   "ro", "ro", "🇷🇴", "Română",       True),
    ("Swahili",    "sw", "sw", "🇰🇪", "Kiswahili",    False),
    ("Hausa",      "ha", "ha", "🇳🇬", "Hausa",        False),
    ("Yoruba",     "yo", "yo", "🇳🇬", "Yorùbá",       False),
    ("Amharic",    "am", "am", "🇪🇹", "አማርኛ",        False),
    ("Afrikaans",  "af", "af", "🇿🇦", "Afrikaans",    False),
    ("Zulu",       "zu", "zu", "🇿🇦", "isiZulu",      False),
]

# Vertaalde meta-description templates (LABELS[lang]["meta_description"]).
# {title} {rating} {price} {tagline} worden ingevuld met .format(...)
META_DESC = {
    "zh": "{title} — {rating}★ 评分，{price}。{tagline}。诚实的创始人评测，含优点、缺点和投资回报率。",
    "ko": "{title} — {rating}★ 평가, {price}. {tagline}. 장단점과 ROI를 담은 솔직한 창업자 리뷰.",
    "hi": "{title} — {rating}★ रेटिंग, {price}. {tagline}. फायदे, नुकसान और ROI के साथ ईमानदार संस्थापक समीक्षा।",
    "ar": "{title} — {rating}★ تقييم، {price}. {tagline}. مراجعة صادقة من المؤسس مع الإيجابيات والسلبيات والعائد على الاستثمار.",
    "th": "{title} — {rating}★ คะแนน, {price}. {tagline}. รีวิวจากผู้ก่อตั้งอย่างตรงไปตรงมา พร้อมข้อดี ข้อเสีย และ ROI",
    "ru": "{title} — оценка {rating}★, {price}. {tagline}. Честный обзор от основателя с плюсами, минусами и ROI.",
    "cs": "{title} — hodnocení {rating}★, {price}. {tagline}. Upřímná recenze zakladatele s klady, zápory a ROI.",
    "fi": "{title} — {rating}★ arvio, {price}. {tagline}. Rehellinen perustajan arvostelu: hyödyt, haitat ja ROI.",
    "el": "{title} — βαθμολογία {rating}★, {price}. {tagline}. Ειλικρινής κριτική ιδρυτή με πλεονεκτήματα, μειονεκτήματα και ROI.",
    "hu": "{title} — {rating}★ értékelés, {price}. {tagline}. Őszinte alapítói értékelés előnyökkel, hátrányokkal és ROI-val.",
    "ro": "{title} — evaluare {rating}★, {price}. {tagline}. Recenzie sinceră a fondatorului cu avantaje, dezavantaje și ROI.",
    "sw": "{title} — kiwango {rating}★, {price}. {tagline}. Mapitio ya kweli ya mwanzilishi yenye faida, hasara na ROI.",
    "ha": "{title} — kima {rating}★, {price}. {tagline}. Sahihin bita daga wanda ya kafa: fa'idodi, illa da ROI.",
    "yo": "{title} — ìdíwọ̀n {rating}★, {price}. {tagline}. Àtúnyẹ̀wò olódodo láti ọ̀dọ̀ olùdásílẹ̀: àǹfààní, àìní àti ROI.",
    "am": "{title} — {rating}★ ደረጃ, {price}. {tagline}. ከመስራቹ ሐቀኛ ግምገማ ከጥቅሞች፣ ጉዳቶች እና ROI ጋር።",
    "af": "{title} — {rating}★ gradering, {price}. {tagline}. Eerlike stigter-resensie met voordele, nadele en ROI.",
    "zu": "{title} — isilinganiso {rating}★, {price}. {tagline}. Ukubuyekezwa okuqotho komsunguli: izinzuzo, ububi ne-ROI.",
}

# Vertaalde V1-fallback descriptions (LANG_DESCRIPTIONS in generate_article.py)
LANG_DESC = {
    "zh": "{title} 的专业 B2B 分析。ROI 明细、价格比较及 2026 年创始人洞察。",
    "ko": "{title}에 대한 전문 B2B 분석. ROI 분석, 가격 비교 및 2026년 창업자 인사이트.",
    "hi": "{title} का विशेषज्ञ B2B विश्लेषण। ROI विवरण, मूल्य तुलना और 2026 के लिए संस्थापक अंतर्दृष्टि।",
    "ar": "تحليل B2B متخصص لـ {title}. تفصيل العائد على الاستثمار ومقارنة الأسعار ورؤى المؤسسين لعام 2026.",
    "th": "การวิเคราะห์ B2B เชิงลึกของ {title} รายละเอียด ROI การเปรียบเทียบราคา และมุมมองผู้ก่อตั้งสำหรับปี 2026",
    "ru": "Экспертный B2B-анализ {title}. Разбор ROI, сравнение цен и инсайты основателей на 2026 год.",
    "cs": "Odborná B2B analýza {title}. Rozbor ROI, srovnání cen a postřehy zakladatelů pro rok 2026.",
    "fi": "Asiantuntijan B2B-analyysi: {title}. ROI-erittely, hintavertailu ja perustajien näkemykset vuodelle 2026.",
    "el": "Ειδική ανάλυση B2B του {title}. Ανάλυση ROI, σύγκριση τιμών και πληροφορίες ιδρυτών για το 2026.",
    "hu": "Szakértői B2B-elemzés: {title}. ROI-bontás, árösszehasonlítás és alapítói meglátások 2026-ra.",
    "ro": "Analiză B2B expertă a {title}. Detalierea ROI, comparație de prețuri și perspective ale fondatorilor pentru 2026.",
    "sw": "Uchambuzi bingwa wa B2B wa {title}. Maelezo ya ROI, ulinganishaji wa bei na maarifa ya waanzilishi kwa 2026.",
    "ha": "Cikakken bincike na B2B na {title}. Bayanin ROI, kwatanta farashi da fahimtar waɗanda suka kafa don 2026.",
    "yo": "Ìtúpalẹ̀ B2B amọ̀ràn ti {title}. Àlàyé ROI, ìfiwéra iye owó àti òye olùdásílẹ̀ fún 2026.",
    "am": "የ{title} ኤክስፐርት B2B ትንታኔ። የROI ዝርዝር፣ የዋጋ ንጽጽር እና ለ2026 የመስራች ግንዛቤዎች።",
    "af": "Kundige B2B-ontleding van {title}. ROI-uiteensetting, prysvergelyking en stigter-insigte vir 2026.",
    "zu": "Ukuhlaziywa kobuchwepheshe be-B2B kwe-{title}. Ukwehlukaniswa kwe-ROI, ukuqhathaniswa kwamanani nemibono yabasunguli ka-2026.",
}

# ─── Helpers ──────────────────────────────────────────────────────────────
def backup(path: Path) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    shutil.copy2(path, bak)
    return bak

def syntax_check(src: str, name: str) -> bool:
    if not name.endswith(".py"):
        return True
    try:
        compile(src, name, "exec")
        return True
    except SyntaxError as e:
        print(f"   ❌ SyntaxError in {name}: {e}")
        # Schrijf de kapotte versie weg + toon context rond de foutregel
        broken = ROOT / (name + ".broken")
        try:
            broken.write_text(src, encoding="utf-8")
            print(f"   📝 kapotte versie weggeschreven: {broken}")
        except Exception as ex:
            print(f"   (kon .broken niet schrijven: {ex})")
        if e.lineno:
            lines = src.splitlines()
            lo = max(0, e.lineno - 6)
            hi = min(len(lines), e.lineno + 3)
            print(f"   ── context regels {lo + 1}–{hi} ──")
            for i in range(lo, hi):
                marker = " >>" if (i + 1) == e.lineno else "   "
                print(f"   {marker} {i + 1:5d}| {lines[i]}")
        return False

def _insert_at_dict_start(src: str, anchor: str, insert: str) -> tuple[str, bool]:
    """Vind `anchor` (bv. 'LANG_MAP_SUFFIX = {') en plak `insert` direct ná de
    openings-{. Zo hoeven we GEEN braces te tellen — robuust tegen f-strings en
    accolades in waarden ({brand}, {width:>{n}} enz.). Nieuwe entries eindigen op
    een komma, de bestaande entries volgen erna → altijd geldige syntax."""
    start = src.find(anchor)
    if start == -1:
        return src, False
    brace = src.index("{", start)
    return src[:brace + 1] + insert + src[brace + 1:], True

# ─── 1. b2b/index.html — filterknoppen ────────────────────────────────────
def patch_filter_buttons(src: str) -> tuple[str, bool, str]:
    if "filterLang(this,'zh')" in src:
        return src, False, "knoppen al aanwezig"
    # zoek de laatste bestaande taalknop (vi) en plak de nieuwe erna
    m = re.search(r"<button class=\"filter-btn\"[^>]*filterLang\(this,'vi'\)[^>]*>.*?</button>", src)
    if not m:
        return src, False, "anker 'vi'-knop NIET gevonden"
    buttons = "\n".join(
        f"<button class=\"filter-btn\" onclick=\"filterLang(this,'{code}')\">{flag} {native}</button>"
        for (_en, code, _iso, flag, native, _eu) in NEW_LANGS
    )
    new = src[:m.end()] + "\n" + buttons + src[m.end():]
    return new, True, f"{len(NEW_LANGS)} knoppen toegevoegd na 'vi'"

# ─── 2. review_template.py ────────────────────────────────────────────────
def patch_lang_map_suffix(src: str) -> tuple[str, bool, str]:
    if '"-zh"' in src:
        return src, False, "al uitgebreid"
    entries = "\n    " + " ".join(f'"-{c}": "{iso}",' for (_e, c, iso, *_r) in NEW_LANGS)
    new, ok = _insert_at_dict_start(src, "LANG_MAP_SUFFIX = {", entries)
    return (new, True, "nieuwe suffixes toegevoegd") if ok else (src, False, "LANG_MAP_SUFFIX NIET gevonden")

def _label_block(code: str, en_name: str) -> str:
    md = META_DESC[code]
    return f'''    "{code}": {{
        "cta_main": "Try {{brand}} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {{brand}}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {{reviews}} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{md}",
    }},
'''

def patch_labels(src: str) -> tuple[str, bool, str]:
    if '"zh": {' in src or '"zh":{' in src:
        return src, False, "LABELS al uitgebreid"
    if "LABELS = {" not in src:
        return src, False, "LABELS-dict NIET gevonden"
    blocks = "\n" + "".join(_label_block(c, en) for (en, c, *_r) in NEW_LANGS)
    new, ok = _insert_at_dict_start(src, "LABELS = {", blocks)
    return (new, True, f"{len(NEW_LANGS)} LABELS-subdicts toegevoegd") if ok else (src, False, "LABELS-dict NIET gevonden")

# ─── 3. generate_article.py ───────────────────────────────────────────────
def patch_lang_map_v1(src: str) -> tuple[str, bool, str]:
    if '"-zh"' in src:
        return src, False, "al uitgebreid"
    entries = " ".join(f'"-{c}": "{iso}",' for (_e, c, iso, *_r) in NEW_LANGS) + " "
    new, ok = _insert_at_dict_start(src, "lang_map = {", entries)
    return (new, True, "lang_map uitgebreid") if ok else (src, False, "lang_map NIET gevonden")

def patch_lang_descriptions(src: str) -> tuple[str, bool, str]:
    if "LANG_DESCRIPTIONS = {" not in src:
        return src, False, "bestaat niet in deze file — overgeslagen (geen probleem; V2-pad gebruikt LABELS)"
    if '"zh":' in src.split("LANG_DESCRIPTIONS", 1)[1][:4000]:
        return src, False, "al uitgebreid"
    entries = "\n" + "".join(f'    "{c}": "{LANG_DESC[c]}",\n' for (_e, c, *_r) in NEW_LANGS)
    new, ok = _insert_at_dict_start(src, "LANG_DESCRIPTIONS = {", entries)
    return (new, True, f"{len(NEW_LANGS)} descriptions toegevoegd") if ok else (src, False, "LANG_DESCRIPTIONS NIET gevonden")

# ─── Runner ───────────────────────────────────────────────────────────────
def run(rel: str, steps, apply: bool):
    target = ROOT / rel
    print(f"\n📦 {rel}")
    if not target.exists():
        print(f"   ⏭️  bestaat niet: {target}")
        return
    src = target.read_text(encoding="utf-8")
    original = src
    for label, fn in steps:
        src, changed, msg = fn(src)
        mark = "✅" if changed else "⏭️ "
        print(f"   {mark} {label} — {msg}")
    if src == original:
        print("   ℹ️  niets te wijzigen.")
        return
    if not syntax_check(src, target.name):
        print("   ❌ syntaxcheck gefaald — NIET geschreven.")
        return
    if apply:
        bak = backup(target)
        target.write_text(src, encoding="utf-8")
        print(f"   💾 geschreven (backup: {bak.name})")
    else:
        print("   👀 DRY-RUN — zou geschreven worden (gebruik --apply)")

def main():
    apply = "--apply" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    global ROOT
    if paths:
        ROOT = Path(paths[0])
    print("🌍 add_languages.py  —  17 talen toevoegen")
    print("=" * 60)
    print(f"ROOT = {ROOT}")
    print(f"MODUS = {'APPLY (schrijft)' if apply else 'DRY-RUN (schrijft niets)'}")

    run("b2b/index.html", [
        ("filterknoppen toevoegen", patch_filter_buttons),
    ], apply)

    run("review_template.py", [
        ("LANG_MAP_SUFFIX uitbreiden", patch_lang_map_suffix),
        ("LABELS-subdicts toevoegen", patch_labels),
    ], apply)

    run("generate_article.py", [
        ("lang_map uitbreiden", patch_lang_map_v1),
        ("LANG_DESCRIPTIONS uitbreiden", patch_lang_descriptions),
    ], apply)

    print("\n" + "=" * 60)
    print("Klaar. Bij DRY-RUN: check de ✅/⏭️ hierboven en stuur ze door.")
    print("Daarna: python3 add_languages.py --apply")

if __name__ == "__main__":
    main()
