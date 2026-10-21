"""Gebied 4: bijna-identieke pagina's en sjabloonaandeel.

Methode:
- zichtbare tekst -> woord-5-shingles (kleine letters, alleen letters/cijfers)
- shingles die op >= BOILER van alle pagina's van dezelfde site voorkomen
  gelden als sjabloon (menu, footer, disclosure) en tellen niet mee
- Jaccard op de overgebleven 'eigen' shingles, per paar
- sjabloonaandeel = deel van de shingles van een pagina dat sjabloon is

Paren:
  A. binnen elke site: indexeerbare pagina's onderling
  B. tussen sites: indexeerbare pagina's van site X tegen indexeerbare van site Y
     (beide zelf-canonical = dubbele content over domeinen)
  C. AIBM-kopie met canonical naar zuster tegen het canonical-doel

Uitvoer: $AUDIT_OUT/04_similarity.json + samenvatting op stdout.
"""
import collections
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import SITES, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

BOILER = 0.30
K = 5
THRESH = float(__import__("os").environ.get("SIM_THRESH", "0.30"))

idx = load_index()


def shingles(text):
    w = re.findall(r"[a-z0-9$€£%]+", text.lower())
    return {" ".join(w[i:i + K]) for i in range(max(0, len(w) - K + 1))}


def is_indexable(r):
    if r["rel"] == "404.html" or noindex(r) or r["refresh"]:
        return False
    if r["canonicals"]:
        t = norm_url(r["canonicals"][0])
        if t != norm_url(r["url"]):
            s, f, how = url_to_file(t)
            return bool(f and str(f) == r["file"])
    return True


SH = {}
OWN = {}
TPL = {}
for site, recs in idx.items():
    df = collections.Counter()
    for r in recs:
        s = shingles(r["text"])
        SH[r["url"]] = s
        df.update(s)
    n = len(recs)
    boiler = {s for s, c in df.items() if c >= BOILER * n}
    for r in recs:
        s = SH[r["url"]]
        own = s - boiler
        OWN[r["url"]] = own
        TPL[r["url"]] = (1 - len(own) / len(s)) if s else 1.0

# globale sjabloon-shingles (gedeeld over sites: zelfde footer/nav-teksten)
gdf = collections.Counter()
for u, s in OWN.items():
    gdf.update(s)
ALLN = len(OWN)


def jac(a, b):
    if not a or not b:
        return 0.0
    i = len(a & b)
    return i / (len(a) + len(b) - i)


def containment(a, b):
    """deel van a dat ook in b staat"""
    return len(a & b) / len(a) if a else 0.0


res = {"params": {"k": K, "boiler": BOILER, "drempel": THRESH}}
indexable = {site: [r for r in recs if is_indexable(r)] for site, recs in idx.items()}

# A: binnen site
for site, recs in indexable.items():
    pairs = []
    # inverted index voor snelheid
    inv = collections.defaultdict(set)
    for i, r in enumerate(recs):
        for s in OWN[r["url"]]:
            inv[s].add(i)
    cand = collections.Counter()
    for s, ids in inv.items():
        if len(ids) > 60:
            continue
        ids = sorted(ids)
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                cand[(ids[a], ids[b])] += 1
    for (a, b), c in cand.items():
        ra, rb = recs[a], recs[b]
        j = jac(OWN[ra["url"]], OWN[rb["url"]])
        if j >= THRESH:
            pairs.append((round(j, 3), ra["url"], rb["url"], len(OWN[ra["url"]]), len(OWN[rb["url"]])))
    pairs.sort(reverse=True)
    tpl = sorted(((round(TPL[r["url"]], 3), r["url"], r["words"], len(OWN[r["url"]])) for r in recs), reverse=True)
    res[f"A_{site}"] = {"paren_boven_drempel": pairs,
                        "sjabloonaandeel_top": tpl[:40],
                        "sjabloonaandeel_gt_80pct": [t for t in tpl if t[0] > 0.80],
                        "weinig_eigen_shingles_lt150": sorted([t for t in tpl if t[3] < 150], key=lambda x: x[3])}
    print(f"A {site}: {len(recs)} indexeerbaar, {len(pairs)} paren >= {THRESH}, "
          f"{len(res[f'A_{site}']['sjabloonaandeel_gt_80pct'])} met sjabloonaandeel > 80%, "
          f"{len(res[f'A_{site}']['weinig_eigen_shingles_lt150'])} met < 150 eigen shingles")

# B: tussen sites (beide indexeerbaar)
sites = list(SITES)
allrecs = [(s, r) for s in sites for r in indexable[s]]
inv = collections.defaultdict(set)
for i, (s, r) in enumerate(allrecs):
    for sh in OWN[r["url"]]:
        inv[sh].add(i)
cand = collections.Counter()
for sh, ids in inv.items():
    if len(ids) > 80:
        continue
    ids = sorted(ids)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            if allrecs[ids[a]][0] != allrecs[ids[b]][0]:
                cand[(ids[a], ids[b])] += 1
cross = []
for (a, b), c in cand.items():
    if c < 20:
        continue
    ua, ub = allrecs[a][1]["url"], allrecs[b][1]["url"]
    j = jac(OWN[ua], OWN[ub])
    ca = containment(OWN[ua], OWN[ub])
    cb = containment(OWN[ub], OWN[ua])
    if j >= 0.30 or max(ca, cb) >= 0.6:
        cross.append((round(j, 3), round(ca, 3), round(cb, 3), ua, ub))
cross.sort(reverse=True)
res["B_tussen_sites_beide_indexeerbaar"] = cross
print(f"B tussen sites (beide indexeerbaar): {len(cross)} paren met Jaccard >= 0.30 of containment >= 0.6")
print("   waarvan Jaccard >= 0.5:", sum(1 for x in cross if x[0] >= 0.5))

# C: AIBM-kopie -> canonical-doel
copies = []
for r in idx["AIBM"]:
    if not r["canonicals"]:
        continue
    t = r["canonicals"][0]
    s, f, how = url_to_file(t)
    if s and s != "AIBM" and f:
        trec = next((x for x in idx[s] if x["file"] == str(f)), None)
        if trec:
            a, b = OWN[r["url"]], OWN[trec["url"]]
            # shingles vergelijken zonder site-sjabloon, dus eigen tekst
            copies.append((round(jac(a, b), 3), round(containment(a, b), 3), r["url"], trec["url"], r["words"], trec["words"],
                           "noindex" if noindex(r) else "index"))
copies.sort()
res["C_aibm_kopie_vs_zuster"] = copies
bins = collections.Counter()
for c in copies:
    bins["containment >= 0.9" if c[1] >= 0.9 else "0.6-0.9" if c[1] >= 0.6 else "0.3-0.6" if c[1] >= 0.3 else "< 0.3"] += 1
res["C_verdeling_containment"] = dict(bins)
print(f"C AIBM-kopie vs zuster: {len(copies)} paren; containment (deel AIBM-tekst dat op zuster staat): {dict(bins)}")

write_json("04_similarity.json", res)
