"""Gebied 4 (aanvulling): kopstructuur (H2-skelet) van indexeerbare reviewpagina's.

Productnaam -> X, cijfers -> 0. Telt hoeveel reviews exact hetzelfde H2-skelet delen,
per site en over de vier sites heen. Een groot aandeel identieke skeletten is een
technisch zichtbaar teken van geschaalde sjabloonpagina's.

Uitvoer: $AUDIT_OUT/10_heading_skeleton.json + samenvatting op stdout.
"""
import collections
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
from lib import load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

idx = load_index()


def is_indexable(r):
    if r["rel"] == "404.html" or noindex(r) or r["refresh"]:
        return False
    if r["canonicals"] and norm_url(r["canonicals"][0]) != norm_url(r["url"]):
        s, f, how = url_to_file(r["canonicals"][0])
        return bool(f and str(f) == r["file"])
    return True


def name_of(r):
    h = r["h1"][0] if r["h1"] else ""
    m = re.match(r"(.+?)\s+Review\b", h)
    return m.group(1).strip() if m else None


res = {}
allsk = collections.Counter()
allh2 = collections.Counter()
nrev = 0
for site, recs in idx.items():
    sk = collections.Counter()
    h2c = collections.Counter()
    n = 0
    for r in recs:
        if not (is_indexable(r) and re.search(r"-review(\.html|/)$", r["url"])):
            continue
        n += 1
        soup = BeautifulSoup(Path(r["file"]).read_text(errors="replace"), "lxml")
        nm = name_of(r)
        hs = []
        for h in soup.find_all("h2"):
            t = h.get_text(" ", strip=True)
            if nm:
                t = re.sub(re.escape(nm), "X", t, flags=re.I)
            t = re.sub(r"\d+", "0", t)
            hs.append(t)
        sk[tuple(hs)] += 1
        h2c.update(set(hs))
    nrev += n
    allsk.update(sk)
    allh2.update(h2c)
    top = sk.most_common(3)
    res[site] = {"reviews": n, "distinct_skeletten": len(sk),
                 "grootste_groep_identiek": top[0][1] if top else 0,
                 "top_skeletten": [(c, list(s)) for s, c in top],
                 "h2_op_ge_50pct": [(h, c) for h, c in h2c.most_common() if c >= 0.5 * n]}
    print(f"{site}: {n} indexeerbare reviews, {len(sk)} verschillende H2-skeletten, grootste identieke groep {res[site]['grootste_groep_identiek']}")
    print("    H2's op >= 50% van de reviews:", [(h[:40], c) for h, c in res[site]["h2_op_ge_50pct"]][:14])
res["over_vier_sites"] = {"reviews": nrev, "h2_op_ge_50pct": [(h, c) for h, c in allh2.most_common() if c >= 0.5 * nrev]}
print("\nOver vier sites:", nrev, "reviews; H2's op >= 50%:", [(h[:40], c) for h, c in res["over_vier_sites"]["h2_op_ge_50pct"]])
write_json("10_heading_skeleton.json", res)
