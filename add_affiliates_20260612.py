#!/usr/bin/env python3
"""Voegt 9 NIEUWE affiliates toe aan de ARTIKELGENERATOR (=> ook in /b2b/ filter + reviews):
Bokun, Shiftie, Marketing 360, SignNow, Gravity Forms, Goflow, Readymode, Weave, Navan. (Batch 12 juni 2026)
Naar VAULT/TOPICS/COMPETITORS/_LOGO_DOMAIN (generate_article.py) + AFFILIATE/_LOGO_DOMAIN
(review_template.py). Brace-aware insert vlak voor de sluit-}. Idempotent (slaat bestaande
keys over). Backup + py_compile-gate + dry-run default. Schrijf met --apply.
Zelfde patroon als add_affiliates_engine4.py (Emergent/Iconosquare/Increff, 2 juni)."""
import re, sys, shutil, datetime, py_compile, tempfile

APPLY = "--apply" in sys.argv
GEN = "/root/felix_hq/generate_article.py"
RT  = "/root/felix_hq/review_template.py"

NEW = {
    "Bokun": {
        "url": "https://join.bokun.io/krrda8zfzjxg",
        "domain": "bokun.io", "category": "Booking Software", "color": "#0D9488",
        "icon": "🎟️", "letter": "B", "badge": "Demo", "price": "From $49/mo",
        "rating": "4.5", "reviews": "400",
        "tagline": "Booking management for tours & activities, by Tripadvisor",
        "competitors": ["FareHarbor","Rezdy","Checkfront","Peek Pro","TrekkSoft","Xola"],
        "topics": ["tour-booking-software","activity-booking-system","reservation-management-software",
            "fareharbor-alternative","rezdy-alternative","online-booking-platform",
            "tour-operator-software","channel-manager-tours","experience-business-software"],
    },
    "Shiftie": {
        "url": "https://try.shiftie.co/vndu93lvag6m",
        "domain": "shiftie.co", "category": "Scheduling", "color": "#8B5CF6",
        "icon": "🗓️", "letter": "S", "badge": "Free trial", "price": "From $2/user/mo",
        "rating": "4.6", "reviews": "150",
        "tagline": "Staff scheduling & team management without the spreadsheet headache",
        "competitors": ["Deputy","When I Work","Sling","Homebase","7shifts","Planday"],
        "topics": ["staff-scheduling-software","employee-rota-software","shift-planning-app",
            "deputy-alternative","when-i-work-alternative","clock-in-software",
            "team-scheduling-tool","leave-management-software","workforce-scheduling"],
    },
    "Marketing 360": {
        "url": "https://marketing360.partnerlinks.io/6d40krecy1fg",
        "domain": "marketing360.com", "category": "Marketing Platform", "color": "#2563EB",
        "icon": "📣", "letter": "M", "badge": "Demo", "price": "Custom",
        "rating": "4.4", "reviews": "1100",
        "tagline": "All-in-one marketing platform for small business, with real humans to help",
        "competitors": ["HubSpot","Thryv","Vendasta","Keap","GoHighLevel","Constant Contact"],
        "topics": ["all-in-one-marketing-platform","small-business-marketing-software",
            "thryv-alternative","keap-alternative","crm-with-marketing","reputation-management-software",
            "local-business-marketing","marketing-services-platform"],
    },
    "SignNow": {
        "url": "https://partnerstack.signnow.com/gfoy0vr9uwnr",
        "domain": "signnow.com", "category": "E-signature", "color": "#16A34A",
        "icon": "✍️", "letter": "S", "badge": "Free trial", "price": "From $8/user/mo",
        "rating": "4.6", "reviews": "2500",
        "tagline": "Electronic signatures & custom eSignature workflows by airSlate",
        "competitors": ["DocuSign","PandaDoc","Adobe Sign","Dropbox Sign","Alohi","Jotform Sign"],
        "topics": ["electronic-signature-software","docusign-alternative","esignature-workflows",
            "pandadoc-alternative","sign-documents-online","contract-signing-software",
            "esign-api","document-workflow-automation","adobe-sign-alternative"],
    },
    "Gravity Forms": {
        "url": "https://try.gravity.com/8odrg2wkes2d",
        "domain": "gravity.com", "category": "WordPress", "color": "#F15A29",
        "icon": "📝", "letter": "G", "badge": "Licenses", "price": "From $59/yr",
        "rating": "4.7", "reviews": "1800",
        "tagline": "The gold standard in WordPress forms, surveys & workflows",
        "competitors": ["WPForms","Typeform","Jotform","Formidable Forms","Ninja Forms","Fluent Forms"],
        "topics": ["wordpress-form-plugin","gravity-forms-review","wpforms-alternative",
            "form-builder-wordpress","survey-plugin-wordpress","conditional-logic-forms",
            "typeform-alternative","wordpress-workflow-automation","lead-capture-forms"],
    },
    "Goflow": {
        "url": "https://ps.goflow.com/50ln3o9ky3ie",
        "domain": "goflow.com", "category": "E-commerce Operations", "color": "#0891B2",
        "icon": "🔄", "letter": "G", "badge": "Demo", "price": "Custom",
        "rating": "4.6", "reviews": "200",
        "tagline": "Multichannel e-commerce ops: orders, inventory, listings & shipping",
        "competitors": ["Sellbrite","ChannelAdvisor","Linnworks","Zentail","Listing Mirror","Skubana"],
        "topics": ["multichannel-ecommerce-software","marketplace-management-software",
            "sellbrite-alternative","order-management-system","inventory-sync-software",
            "channeladvisor-alternative","amazon-walmart-integration","ecommerce-listings-management"],
    },
    "Readymode": {
        "url": "https://try.readymode.com/w9q86uhvjvzd",
        "domain": "readymode.com", "category": "Call Center", "color": "#DC2626",
        "icon": "☎️", "letter": "R", "badge": "Demo", "price": "Custom",
        "rating": "4.4", "reviews": "350",
        "tagline": "Outbound customer engagement with AI-powered predictive dialing",
        "competitors": ["Five9","Convoso","CallTools","PhoneBurner","Mojo Dialer","Kixie"],
        "topics": ["predictive-dialer-software","outbound-call-center-software","ai-dialer",
            "convoso-alternative","phoneburner-alternative","sales-dialer-platform",
            "call-center-crm","tcpa-compliant-dialer","cold-calling-software"],
    },
    "Weave": {
        "url": "https://partnerstack.getweave.com/6ofmdour3p3q",
        "domain": "getweave.com", "category": "Practice Communication", "color": "#10B981",
        "icon": "🪡", "letter": "W", "badge": "Demo", "price": "Custom",
        "rating": "4.5", "reviews": "500",
        "tagline": "Phone, texting, payments & reviews for small practices in one platform",
        "competitors": ["Podium","Solutionreach","NexHealth","Birdeye","RevenueWell","Demandforce"],
        "topics": ["dental-practice-software","patient-communication-software","podium-alternative",
            "medical-office-phone-system","appointment-reminder-software","practice-texting-software",
            "solutionreach-alternative","healthcare-communication-platform","review-management-practices"],
    },
    "Navan": {
        "url": "https://get.navan.com/onj1xewpcdit",
        "domain": "navan.com", "category": "Travel & Expense", "color": "#111827",
        "icon": "✈️", "letter": "N", "badge": "Free to start", "price": "Free / custom",
        "rating": "4.6", "reviews": "8000",
        "tagline": "Business travel booking & expense management in one platform",
        "competitors": ["SAP Concur","Expensify","Ramp","Brex","TravelPerk","Egencia"],
        "topics": ["travel-expense-software","corporate-travel-management","concur-alternative",
            "expensify-alternative","business-travel-booking","expense-report-automation",
            "travelperk-alternative","spend-management-platform","t-and-e-software"],
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
