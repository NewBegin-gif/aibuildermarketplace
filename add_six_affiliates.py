#!/usr/bin/env python3
"""Voegt 6 NIEUWE affiliates toe aan de ARTIKELGENERATOR (=> ook in /b2b/ filter + reviews):
Katana MRP, Process Street, Gusto, Bright Data, SmartSuite, Melio.
Naar VAULT/TOPICS/COMPETITORS/_LOGO_DOMAIN (generate_article.py) + AFFILIATE/_LOGO_DOMAIN
(review_template.py). Brace-aware insert vlak voor de sluit-}. Idempotent (slaat bestaande
keys over). Backup + py_compile-gate + dry-run default. Schrijf met --apply.
Zelfde patroon als add_affiliates_engine4.py (Emergent/Iconosquare/Increff, 2 juni)."""
import re, sys, shutil, datetime, py_compile, tempfile

APPLY = "--apply" in sys.argv
GEN = "/root/felix_hq/generate_article.py"
RT  = "/root/felix_hq/review_template.py"

NEW = {
    "Katana MRP": {
        "url": "https://psref.katanamrp.com/gn4sa2lpjjph",
        "domain": "katanamrp.com", "category": "Operations", "color": "#F97316",
        "icon": "🏭", "letter": "K", "badge": "Demo", "price": "From $179/mo",
        "rating": "4.6", "reviews": "1100",
        "tagline": "Cloud manufacturing & inventory platform for product businesses",
        "competitors": ["Cin7","Fishbowl","MRPeasy","Unleashed","NetSuite","Odoo"],
        "topics": ["manufacturing-erp-software","inventory-management-software","mrp-software",
            "production-planning-software","shop-floor-control-software","bill-of-materials-software",
            "small-manufacturer-erp","ecommerce-inventory-sync","made-to-order-manufacturing-software",
            "batch-production-software","cin7-alternative","fishbowl-alternative",
            "warehouse-inventory-software","d2c-manufacturing-software"],
    },
    "Process Street": {
        "url": "https://get.process.st/hyrxoou4prfc",
        "domain": "process.st", "category": "Workflow", "color": "#2563EB",
        "icon": "✅", "letter": "P", "badge": "Free trial", "price": "From $100/mo",
        "rating": "4.6", "reviews": "600",
        "tagline": "AI-powered checklists, SOPs & workflows for recurring team work",
        "competitors": ["Trainual","SweetProcess","Tallyfy","Pipefy","Asana","ClickUp"],
        "topics": ["sop-software","checklist-software","workflow-management-software",
            "process-documentation-tool","employee-onboarding-software","recurring-task-software",
            "business-process-management-software","standard-operating-procedures-software",
            "trainual-alternative","process-automation-tool","team-runbook-software",
            "compliance-checklist-software","client-onboarding-workflow-software"],
    },
    "Gusto": {
        "url": "https://get.gusto.com/bz0jei7y1zzh",
        "domain": "gusto.com", "category": "HR & Payroll", "color": "#F45D48",
        "icon": "💼", "letter": "G", "badge": "Free trial", "price": "From $49/mo",
        "rating": "4.7", "reviews": "3800",
        "tagline": "Payroll, benefits & HR for small businesses — run payroll in clicks",
        "competitors": ["Rippling","ADP","Paychex","OnPay","Deel","QuickBooks Payroll"],
        "topics": ["payroll-software","small-business-payroll-software","hr-software-small-business",
            "employee-benefits-platform","payroll-tax-filing-software","employee-onboarding-software",
            "contractor-payments-software","rippling-alternative","adp-alternative",
            "time-tracking-payroll-software","payroll-automation-software","startup-payroll-software"],
    },
    "Bright Data": {
        "url": "https://get.brightdata.com/vnvncunqr9rj",
        "domain": "brightdata.com", "category": "Data & Scraping", "color": "#3B82F6",
        "icon": "🌐", "letter": "B", "badge": "Free trial", "price": "Pay as you go",
        "rating": "4.6", "reviews": "700",
        "tagline": "Web data platform: proxies, scraping APIs & ready-made datasets",
        "competitors": ["Oxylabs","Decodo","Zyte","Apify","ScraperAPI","SOAX"],
        "topics": ["web-scraping-api","proxy-network-software","data-collection-platform",
            "residential-proxies-service","serp-api","web-data-for-ai-training",
            "dataset-marketplace","price-monitoring-data-tool","oxylabs-alternative",
            "apify-alternative","market-research-data-tool","web-unlocker-software"],
    },
    "SmartSuite": {
        "url": "https://partners.smartsuite.com/3o9qow98qlja",
        "domain": "smartsuite.com", "category": "Work Management", "color": "#7C3AED",
        "icon": "🗂️", "letter": "S", "badge": "Free plan", "price": "From $10/user/mo",
        "rating": "4.8", "reviews": "1200",
        "tagline": "One flexible platform to plan, track & automate any business process",
        "competitors": ["Airtable","monday.com","ClickUp","Notion","Asana","Smartsheet"],
        "topics": ["work-management-software","no-code-database-software","project-management-platform",
            "business-process-software","airtable-alternative","monday-alternative",
            "team-collaboration-software","workflow-automation-platform","crm-builder-software",
            "operations-management-software","task-management-software","notion-alternative"],
    },
    "Melio": {
        "url": "https://affiliates.meliopayments.com/3k7t5bt87uuu",
        "domain": "meliopayments.com", "category": "Payments", "color": "#10B981",
        "icon": "💸", "letter": "M", "badge": "Free to start", "price": "Free / pay per use",
        "rating": "4.5", "reviews": "500",
        "tagline": "Effortless B2B bill payments & receivables for small businesses",
        "competitors": ["Bill.com","Ramp","Tipalti","Stampli","Plooto","QuickBooks"],
        "topics": ["accounts-payable-software","b2b-payments-platform","bill-payment-software",
            "vendor-payment-software","accounts-receivable-software","bill-com-alternative",
            "small-business-payments-software","pay-vendors-by-card","invoice-payment-software",
            "cash-flow-management-tool","ap-automation-software"],
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
