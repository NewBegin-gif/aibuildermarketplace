#!/usr/bin/env python3
"""Voegt 6 NIEUWE affiliates toe aan de ARTIKELGENERATOR (=> ook in /b2b/ filter + reviews):
Quo, Flocksy, Shippo, TaxCycle, Alohi, WebCatalog. (Batch 11 juni 2026)
Naar VAULT/TOPICS/COMPETITORS/_LOGO_DOMAIN (generate_article.py) + AFFILIATE/_LOGO_DOMAIN
(review_template.py). Brace-aware insert vlak voor de sluit-}. Idempotent (slaat bestaande
keys over). Backup + py_compile-gate + dry-run default. Schrijf met --apply.
Zelfde patroon als add_affiliates_engine4.py (Emergent/Iconosquare/Increff, 2 juni)."""
import re, sys, shutil, datetime, py_compile, tempfile

APPLY = "--apply" in sys.argv
GEN = "/root/felix_hq/generate_article.py"
RT  = "/root/felix_hq/review_template.py"

NEW = {
    "Quo": {
        "url": "https://get.quo.com/aibuildermarketplace",
        "domain": "quo.com", "category": "Business Phone", "color": "#6366F1",
        "icon": "📞", "letter": "Q", "badge": "Free trial", "price": "From $15/mo",
        "rating": "4.7", "reviews": "2000",
        "tagline": "Modern business phone system (ex-OpenPhone) for startups & small teams",
        "competitors": ["Aircall","CloudTalk","KrispCall","Dialpad","RingCentral","Grasshopper"],
        "topics": ["business-phone-system","voip-for-startups","shared-phone-number-software",
            "ai-call-summaries-software","openphone-alternative","business-texting-software",
            "virtual-phone-number-app","aircall-alternative","dialpad-alternative",
            "small-business-phone-app","call-recording-software","team-phone-system"],
    },
    "Flocksy": {
        "url": "https://join.flocksy.com/gkm4cd2nj6km",
        "domain": "flocksy.com", "category": "Design Services", "color": "#F59E0B",
        "icon": "🎨", "letter": "F", "badge": "Flat fee", "price": "From $499/mo",
        "rating": "4.6", "reviews": "350",
        "tagline": "Unlimited creative team subscription: design, video & motion graphics",
        "competitors": ["Design Pickle","Penji","Kimp","ManyPixels","99designs","Superside"],
        "topics": ["unlimited-graphic-design-service","design-subscription-service",
            "flat-fee-design-agency","video-editing-subscription","design-pickle-alternative",
            "penji-alternative","outsourced-design-team","marketing-design-service",
            "motion-graphics-service","brand-design-subscription","creative-team-as-a-service"],
    },
    "Shippo": {
        "url": "https://try.shippo.com/bt14md940onh",
        "domain": "goshippo.com", "category": "E-commerce Shipping", "color": "#16A34A",
        "icon": "📦", "letter": "S", "badge": "Free plan", "price": "Free / pay per label",
        "rating": "4.6", "reviews": "900",
        "tagline": "Multi-carrier shipping labels & automation for e-commerce",
        "competitors": ["ShipStation","EasyPost","Pirate Ship","Easyship","Stamps.com","ShipBob"],
        "topics": ["shipping-software-ecommerce","multi-carrier-shipping-api",
            "discounted-shipping-labels","shipstation-alternative","shipping-rate-comparison",
            "order-fulfillment-software","shipping-automation-software","easypost-alternative",
            "shopify-shipping-app","shipping-tracking-software","small-business-shipping-software"],
    },
    "TaxCycle": {
        "url": "https://invitation.taxcycle.com/ngza3ochezk9",
        "domain": "taxcycle.com", "category": "Tax Software", "color": "#D97706",
        "icon": "🧾", "letter": "T", "badge": "Demo", "price": "Custom",
        "rating": "4.7", "reviews": "250",
        "tagline": "Professional Canadian tax preparation suite for accountants",
        "competitors": ["Profile","Cantax","DT Max","UFile PRO","CCH iFirm","TaxPrep"],
        "topics": ["canadian-tax-software","professional-tax-preparation-software",
            "t1-tax-software","t2-corporate-tax-software","cra-efile-software",
            "profile-alternative","accountant-tax-suite","tax-workflow-software",
            "taxprep-alternative","bookkeeping-tax-software"],
    },
    "Alohi": {
        "url": "https://ref.alohi.com/i94t0wafno1b",
        "domain": "alohi.com", "category": "Document Workflow", "color": "#0EA5E9",
        "icon": "✍️", "letter": "A", "badge": "Free plan", "price": "From $10/mo",
        "rating": "4.6", "reviews": "600",
        "tagline": "Sign.Plus e-signatures, Fax.Plus faxing & Scan.Plus — secure document workflows",
        "competitors": ["DocuSign","PandaDoc","SignNow","Dropbox Sign","eFax","HelloFax"],
        "topics": ["electronic-signature-software","online-fax-service","docusign-alternative",
            "esignature-for-small-business","document-workflow-software","hipaa-compliant-fax",
            "pandadoc-alternative","sign-documents-online","secure-document-scanning-app",
            "contract-signing-software"],
    },
    "WebCatalog": {
        "url": "https://try.webcatalog.io/powenno3ohno",
        "domain": "webcatalog.io", "category": "Productivity", "color": "#2563EB",
        "icon": "🗂️", "letter": "W", "badge": "Free plan", "price": "Free / paid plans",
        "rating": "4.5", "reviews": "400",
        "tagline": "Turn web apps into desktop apps & manage multiple accounts side by side",
        "competitors": ["Rambox","Station","Ferdium","Shift","Wavebox","Unite"],
        "topics": ["desktop-app-manager","turn-website-into-app","multiple-account-manager",
            "rambox-alternative","shift-alternative","web-app-organizer",
            "productivity-desktop-software","app-launcher-software","manage-multiple-logins",
            "distraction-free-workspace"],
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
