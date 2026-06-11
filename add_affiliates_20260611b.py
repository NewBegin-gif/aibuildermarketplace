#!/usr/bin/env python3
"""Voegt 3 NIEUWE affiliates toe aan de ARTIKELGENERATOR (=> ook in /b2b/ filter + reviews):
Livestorm, Volza, CallHippo. (Batch 11 juni 2026 — avond)
Naar VAULT/TOPICS/COMPETITORS/_LOGO_DOMAIN (generate_article.py) + AFFILIATE/_LOGO_DOMAIN
(review_template.py). Brace-aware insert vlak voor de sluit-}. Idempotent (slaat bestaande
keys over). Backup + py_compile-gate + dry-run default. Schrijf met --apply.
Zelfde patroon als add_affiliates_engine4.py (Emergent/Iconosquare/Increff, 2 juni)."""
import re, sys, shutil, datetime, py_compile, tempfile

APPLY = "--apply" in sys.argv
GEN = "/root/felix_hq/generate_article.py"
RT  = "/root/felix_hq/review_template.py"

NEW = {
    "Livestorm": {
        "url": "https://get.livestorm.co/cfc8vpp5fl59",
        "domain": "livestorm.com", "category": "Webinars", "color": "#6D5DF6",
        "icon": "🎥", "letter": "L", "badge": "Free plan", "price": "From $99/mo",
        "rating": "4.6", "reviews": "1300",
        "tagline": "All-in-one webinar & video engagement platform for marketing teams",
        "competitors": ["Zoom Webinars","WebinarJam","Demio","GoTo Webinar","BigMarker","Zoho Webinar"],
        "topics": ["webinar-software","webinar-platform-for-marketing","browser-based-webinar-tool",
            "automated-webinar-software","zoom-webinars-alternative","demio-alternative",
            "virtual-event-platform","product-demo-software","lead-generation-webinars",
            "webinar-analytics-software","online-event-software"],
    },
    "Volza": {
        "url": "https://partner.volza.com/gfxywibpiht5",
        "domain": "volza.com", "category": "Trade Intelligence", "color": "#0E7490",
        "icon": "🌍", "letter": "V", "badge": "Demo", "price": "From $1500/yr",
        "rating": "4.5", "reviews": "300",
        "tagline": "Export-import trade data: find verified buyers & suppliers in 80+ countries",
        "competitors": ["ImportGenius","Panjiva","Trademap","ImportYeti","Descartes Datamyne","Trademo"],
        "topics": ["export-import-data-platform","trade-intelligence-software","find-international-buyers",
            "shipment-data-search","importgenius-alternative","panjiva-alternative",
            "global-trade-data-software","supplier-discovery-tool","export-market-research",
            "customs-data-platform","b2b-trade-leads"],
    },
    "CallHippo": {
        "url": "https://join.callhippo.com/acacgh9cnvo1",
        "domain": "callhippo.com", "category": "Business Phone", "color": "#4F46E5",
        "icon": "📱", "letter": "C", "badge": "Free trial", "price": "From $18/mo",
        "rating": "4.4", "reviews": "600",
        "tagline": "AI-driven business phone system with virtual numbers in 50+ countries",
        "competitors": ["Aircall","CloudTalk","KrispCall","Quo","RingCentral","JustCall"],
        "topics": ["virtual-phone-number-software","ai-call-center-software","power-dialer-software",
            "business-voip-system","aircall-alternative","justcall-alternative",
            "international-business-numbers","call-analytics-software","sales-dialer-software",
            "support-call-software","cloudtalk-alternative"],
    },
}

# ---------- helpers ----------
def backup(p):
    b = p + ".bak." + datetime.datetime.now().strftime("%H%M%S")
    shutil.copy2(p, b); return b

def find_dict_span(src, varname):
    m = re.search(r'(?m)^' + re.escape(varname) + r'\s*=\s*\{', src)
    if not m:
        return None
    i = src.index("{", m.start())
    depth = 0; instr = None; esc = False; j = i
    while j < len(src):
        c = src[j]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == instr: instr = None
        else:
            if c in "\"'": instr = c
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return (i, j)
        j += 1
    return None

def has_key(dict_text, key):
    return re.search(r'["\']' + re.escape(key) + r'["\']\s*:', dict_text) is not None

def insert_before_close(src, span, new_lines):
    open_idx, close_idx = span
    before = src[:close_idx]
    stripped = before.rstrip()
    if not stripped.endswith(",") and not stripped.endswith("{"):
        before = stripped + ",\n"
    else:
        before = stripped + "\n"
    block = "".join("    " + ln + "\n" for ln in new_lines)
    return before + block + src[close_idx:]

def pylist(items):
    return "[" + ", ".join("'" + x.replace("'", "\\'") + "'" for x in items) + "]"

def _q(v):
    return str(v).replace("\\", "\\\\").replace("'", "\\'")

def aff_entry(brand, d):
    svg = ('<svg viewBox="0 0 24 24" width="1em" height="1em" '
           'xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="%s"/>'
           '<text x="12" y="17" font-size="13" font-family="Inter,Arial,sans-serif" '
           'font-weight="700" fill="#fff" text-anchor="middle">%s</text></svg>'
           ) % (d["color"], d["letter"])
    return ("'%s': {'badge':'%s','category':'%s','color':'%s','icon':'%s','logo':'%s',"
            "'price':'%s','rating':'%s','reviews':'%s','tagline':'%s','url':'%s'},"
            ) % (_q(brand), _q(d["badge"]), _q(d["category"]), _q(d["color"]), _q(d["icon"]), _q(svg),
                 _q(d["price"]), _q(d["rating"]), _q(d["reviews"]), _q(d["tagline"]), _q(d["url"]))

# ---------- load ----------
gen = open(GEN, encoding="utf-8").read(); gen0 = gen
rt  = open(RT,  encoding="utf-8").read(); rt0 = rt
report = []

def patch_gen_dict(src, var, entries):
    span = find_dict_span(src, var)
    if not span:
        report.append(f"   ❌ {var} niet gevonden in generate_article.py"); return src, 0
    body = src[span[0]:span[1]+1]
    add = [line for line, key in entries if not has_key(body, key)]
    if not add:
        report.append(f"   {var}: niets toe te voegen (alles al aanwezig)"); return src, 0
    report.append(f"   {var}: +{len(add)}")
    return insert_before_close(src, span, add), len(add)

gen, _ = patch_gen_dict(gen, "VAULT", [(f"'{b}': '{d['url']}',", b) for b, d in NEW.items()])
gen, _ = patch_gen_dict(gen, "TOPICS", [(f"'{b}': {pylist(d['topics'])},", b) for b, d in NEW.items()])
gen, _ = patch_gen_dict(gen, "COMPETITORS", [(f"'{b}': {pylist(d['competitors'])},", b) for b, d in NEW.items()])
gen, _ = patch_gen_dict(gen, "_LOGO_DOMAIN", [(f"'{b}': '{d['domain']}',", b) for b, d in NEW.items()])

# review_template.py
span = find_dict_span(rt, "AFFILIATE")
if not span:
    report.append("   ❌ AFFILIATE niet gevonden in review_template.py")
else:
    body = rt[span[0]:span[1]+1]
    add = [aff_entry(b, d) for b, d in NEW.items() if not has_key(body, b)]
    if add:
        report.append(f"   AFFILIATE: +{len(add)}"); rt = insert_before_close(rt, span, add)
    else:
        report.append("   AFFILIATE: niets toe te voegen")

span = find_dict_span(rt, "_LOGO_DOMAIN")
if not span:
    report.append("   ❌ _LOGO_DOMAIN niet gevonden in review_template.py")
else:
    body = rt[span[0]:span[1]+1]
    add = [f"'{b}': '{d['domain']}'," for b, d in NEW.items() if not has_key(body, b)]
    if add:
        report.append(f"   RT._LOGO_DOMAIN: +{len(add)}"); rt = insert_before_close(rt, span, add)
    else:
        report.append("   RT._LOGO_DOMAIN: niets toe te voegen")

# ---------- verify ----------
changed = []
if gen != gen0: changed.append((GEN, gen))
if rt  != rt0:  changed.append((RT, rt))
print("\n".join(report))
for path, content in changed:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(content); tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"❌ py_compile FAALT {path}:\n{e}"); sys.exit(1)
if changed:
    print("✅ py_compile: OK (" + ", ".join(p.split('/')[-1] for p, _ in changed) + ")")
else:
    print("⏭️  niets te wijzigen — alles al aanwezig"); sys.exit(0)
if not APPLY:
    print("\nDRY-RUN — niets geschreven. Voer uit met --apply om te schrijven."); sys.exit(0)
for path, content in changed:
    b = backup(path); open(path, "w", encoding="utf-8").write(content)
    print(f"✅ {path} geschreven. Backup: {b}")
