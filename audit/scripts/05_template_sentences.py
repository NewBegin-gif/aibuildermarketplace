"""Gebied 4 (aanvulling): geschaalde sjablonen en dezelfde paginatypes op meerdere domeinen.

1. Sjabloonzinnen: zinnen die (na normalisatie: cijfers -> 0, productnaam -> X)
   op >= 10% en < 90% van de indexeerbare reviewpagina's van een site staan.
   Menu/footer (>= 90%) telt niet mee. Per pagina: aandeel woorden in zulke zinnen.
2. Zelfde slug/paginatype op meerdere domeinen (tools/, mcp, deals, atlas, finder...)
   met per domein de indexeerstatus.

Uitvoer: $AUDIT_OUT/05_template_sentences.json + samenvatting op stdout.
"""
import collections
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import SITES, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

idx = load_index()


def is_indexable(r):
    if r["rel"] == "404.html" or noindex(r) or r["refresh"]:
        return False
    if r["canonicals"]:
        t = norm_url(r["canonicals"][0])
        if t != norm_url(r["url"]):
            s, f, how = url_to_file(t)
            return bool(f and str(f) == r["file"])
    return True


def is_review(r):
    return bool(re.search(r"-review(\.html|/)$", r["url"]))


def product_name(r):
    h = r["h1"][0] if r["h1"] else (r["titles"][0] if r["titles"] else "")
    m = re.match(r"(.+?)\s+Review\b", h)
    return m.group(1).strip() if m else None


def sentences(text, name):
    if name:
        text = re.sub(re.escape(name), "X", text, flags=re.I)
    text = re.sub(r"\d+([.,]\d+)?", "0", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [re.sub(r"\s+", " ", p.strip().lower()) for p in parts if len(p.split()) >= 6]


res = {}
for site, recs in idx.items():
    revs = [r for r in recs if is_indexable(r) and is_review(r)]
    if not revs:
        continue
    df = collections.Counter()
    sents = {}
    for r in revs:
        ss = sentences(r["text"], product_name(r))
        sents[r["url"]] = ss
        df.update(set(ss))
    n = len(revs)
    tpl = {s: c for s, c in df.items() if 0.10 * n <= c < 0.90 * n}
    per_page = []
    for r in revs:
        ss = sents[r["url"]]
        tw = sum(len(s.split()) for s in ss if s in tpl)
        aw = sum(len(s.split()) for s in ss) or 1
        per_page.append((round(tw / aw, 3), r["url"], aw))
    per_page.sort(reverse=True)
    top = sorted(tpl.items(), key=lambda x: -x[1])[:40]
    shares = [p[0] for p in per_page]
    res[site] = {
        "reviewpaginas_indexeerbaar": n,
        "sjabloonzinnen_aantal": len(tpl),
        "sjabloonzinnen_top": [(c, s[:200]) for s, c in top],
        "aandeel_woorden_in_sjabloonzinnen_mediaan": sorted(shares)[len(shares) // 2] if shares else None,
        "paginas_aandeel_gt_25pct": [p for p in per_page if p[0] > 0.25],
        "per_pagina_top": per_page[:25],
    }
    print(f"{site}: {n} indexeerbare reviews, {len(tpl)} sjabloonzinnen (10-90%), mediaan aandeel {res[site]['aandeel_woorden_in_sjabloonzinnen_mediaan']}, "
          f"{len(res[site]['paginas_aandeel_gt_25pct'])} pagina's > 25%")
    for c, s in res[site]["sjabloonzinnen_top"][:8]:
        print(f"    {c:4d}x  {s[:150]}")

# 2. zelfde slug op meerdere domeinen
def slug(r):
    p = r["rel"]
    p = re.sub(r"/index\.html$", "", p)
    p = re.sub(r"\.html$", "", p)
    p = p.replace("b2b/", "").replace("best/", "best-").replace("build/", "build-")
    return p


slugmap = collections.defaultdict(dict)
for site, recs in idx.items():
    for r in recs:
        st = "index" if is_indexable(r) else ("noindex" if noindex(r) else "canonical-elders" if r["canonicals"] else "overig")
        slugmap[slug(r)][site] = (st, r["url"])
multi = {s: v for s, v in slugmap.items() if len(v) >= 2}
multi_idx = {s: v for s, v in multi.items() if sum(1 for x in v.values() if x[0] == "index") >= 2}
res["slug_op_meerdere_domeinen"] = len(multi)
res["slug_meerdere_domeinen_indexeerbaar_op_2plus"] = sorted(((s, {k: x[0] for k, x in v.items()}) for s, v in multi_idx.items()))
print(f"\nslugs op >= 2 domeinen: {len(multi)}; waarvan op >= 2 domeinen indexeerbaar: {len(multi_idx)}")
for s, v in res["slug_meerdere_domeinen_indexeerbaar_op_2plus"][:60]:
    print("   ", s, v)
write_json("05_template_sentences.json", res)
