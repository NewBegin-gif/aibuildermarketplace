#!/usr/bin/env python3
"""Patcht rebuild_index()-template zodat /b2b/?tool=X de index direct voorfiltert.

Twee wijzigingen in de generator-bron (het .py-bestand in /root/felix_hq dat de
b2b-index-JS bevat, herkenbaar aan "activeTool"):
  1. Fix active-class-clearing van de tool-knoppen: selector
     '.filter-btn[data-tool]' matcht niets (tool-knoppen hebben geen data-tool),
     wordt '.filter-btn[onclick*=filterTool]'.
  2. Voegt na function filterSearch(...) een IIFE toe die ?tool= uit de URL
     leest en de bijbehorende filterknop aanklikt. Matching is tolerant
     (genormaliseerd, exact > prefix), zodat zowel ?tool=Murf als oude links
     als ?tool=emergent-pricing-no werken.

Houdt rekening met f-string-templates (verdubbelt dan automatisch de accolades).
Idempotent (slaat over als URLSearchParams al aanwezig). Backup + py_compile-gate
+ dry-run default. Schrijf met --apply. Wordt zichtbaar op de site bij de
eerstvolgende rebuild van b2b/index.html (uurlijkse/2-uurlijkse cron).
"""
import glob, sys, shutil, datetime, py_compile, tempfile

APPLY = "--apply" in sys.argv

SEL_OLD = ".filter-btn[data-tool]"
SEL_NEW = ".filter-btn[onclick*=filterTool]"

ANCHOR = "function filterSearch(q){searchQ=q;applyFilter();}"

SNIPPET = ("\n        (function(){var v=new URLSearchParams(location.search).get('tool');"
"if(!v)return;"
"var N=function(s){return s.toLowerCase().split('').filter(function(c){return 'abcdefghijklmnopqrstuvwxyz0123456789'.indexOf(c)>-1}).join('')};"
"var nv=N(v),exact=null,pre=null;"
"document.querySelectorAll('.filter-btn').forEach(function(b){"
"var oc=b.getAttribute('onclick')||'';"
"if(oc.indexOf('filterTool')!==0)return;"
"var s=oc.indexOf(String.fromCharCode(39))+1,e=oc.lastIndexOf(String.fromCharCode(39));"
"if(s<=0||e<=s)return;"
"var t=oc.substring(s,e);"
"if(t==='all')return;"
"var nb=N(t);"
"if(nb===nv)exact=exact||b;else if(nb.length>4&&nv.indexOf(nb)===0)pre=pre||b});"
"var hit=exact||pre;if(hit)hit.click()})();")


def dbl(s):
    return s.replace("{", "{{").replace("}", "}}")


def backup(p):
    b = p + ".bak." + datetime.datetime.now().strftime("%H%M%S")
    shutil.copy2(p, b)
    return b


candidates = [p for p in sorted(glob.glob("/root/felix_hq/*.py"))
              if "activeTool" in open(p, encoding="utf-8").read()]
if not candidates:
    print("❌ geen generator-bestand met 'activeTool' gevonden in /root/felix_hq/")
    sys.exit(1)

for path in candidates:
    src = open(path, encoding="utf-8").read()
    orig = src
    report = [f"== {path}"]

    if "URLSearchParams" in src:
        report.append("   al gepatcht — overgeslagen")
        print("\n".join(report))
        continue

    # f-string-template? Dan staan de accolades verdubbeld in de bron.
    if ANCHOR in src:
        anchor, snippet = ANCHOR, SNIPPET
        report.append("   template: normale string")
    elif dbl(ANCHOR) in src:
        anchor, snippet = dbl(ANCHOR), dbl(SNIPPET)
        report.append("   template: f-string (accolades verdubbeld)")
    else:
        report.append("   ❌ anker filterSearch niet gevonden — overgeslagen")
        print("\n".join(report))
        continue

    n_sel = src.count(SEL_OLD)
    if n_sel:
        src = src.replace(SEL_OLD, SEL_NEW)
        report.append(f"   selector-fix active-class: {n_sel}x")
    else:
        report.append("   selector '.filter-btn[data-tool]' niet gevonden (mogelijk al gefixt)")

    src = src.replace(anchor, anchor + snippet, 1)
    report.append("   ?tool=-voorfilter toegevoegd na filterSearch")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(src)
        tmp = tf.name
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        print("\n".join(report))
        print(f"❌ py_compile FAALT — niets geschreven:\n{e}")
        sys.exit(1)
    report.append("   ✅ py_compile: OK")

    if not APPLY:
        report.append("   DRY-RUN — niets geschreven. Voer uit met --apply.")
        print("\n".join(report))
        continue

    b = backup(path)
    open(path, "w", encoding="utf-8").write(src)
    report.append(f"   ✅ geschreven. Backup: {b}")
    print("\n".join(report))
