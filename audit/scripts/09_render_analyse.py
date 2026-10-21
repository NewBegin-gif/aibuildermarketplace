"""Analyse van 09_render.cjs: verschil tussen weergave zonder en met JavaScript.

Signaleert:
- pagina's die zonder JS (bijna) leeg zijn
- title/canonical/robots/H1 die door JS veranderen (cloaking-achtig of risico)
- tekst die alleen met JS verschijnt of alleen zonder JS zichtbaar is
- JS-fouten, horizontale overloop op 412 px (mobiel)

Aanroep: python3 -I audit/scripts/09_render_analyse.py [render.json]
Uitvoer: $AUDIT_OUT/09_render_analyse.json + samenvatting op stdout.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import OUT, write_json  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else str(OUT / "render.json")
data = json.load(open(src))


def words(t):
    return re.findall(r"\w+", (t or "").lower())


def sh(t, k=4):
    w = words(t)
    return {" ".join(w[i:i + k]) for i in range(max(0, len(w) - k + 1))}


out = collections.defaultdict(list)
stats = collections.Counter()
for r in data:
    a, b = r.get("nojs") or {}, r.get("js") or {}
    u = r["url"]
    site = u.split("/")[2]
    stats["pagina's"] += 1
    if "error" in a or "error" in b:
        out["laadfout"].append((u, a.get("error"), b.get("error")))
        continue
    wa, wb = len(words(a["text"])), len(words(b["text"]))
    if wa < 150:
        out["zonder_js_minder_dan_150_woorden"].append((u, wa, wb))
    for k in ("title", "canonical", "robots", "h1"):
        if a.get(k) != b.get(k):
            out[f"js_wijzigt_{k}"].append((u, a.get(k), b.get(k)))
    A, B = sh(a["text"]), sh(b["text"])
    only_js = len(B - A) / len(B) if B else 0
    only_nojs = len(A - B) / len(A) if A else 0
    if only_js > 0.25:
        out["tekst_vooral_met_js"].append((u, round(only_js, 2), wa, wb))
    if only_nojs > 0.25:
        out["tekst_alleen_zonder_js"].append((u, round(only_nojs, 2), wa, wb))
    if b.get("errors"):
        out["js_fouten"].append((u, b["errors"][:2]))
    if b.get("scrollWidth", 0) > 420:
        out["horizontale_overloop_412px"].append((u, b["scrollWidth"]))
    stats[f"{site} woorden zonder js"] += wa
    stats[f"{site} woorden met js"] += wb

res = {"stats": dict(stats), **out}
write_json("09_render_analyse.json", res)
for k, v in stats.items():
    print(f"  {k:45s} {v}")
for k, v in out.items():
    print(f"  -> {k}: {len(v)}")
    for x in v[:5]:
        print("       ", str(x)[:220])
