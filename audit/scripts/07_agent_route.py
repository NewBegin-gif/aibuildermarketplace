"""Gebied 7: agent-/AI-route.

- llms.txt / llms-full.txt per site: elke URL -> bestaat? noindex? canonical elders?
- /api/v1/*.json (AIBM): geldige JSON, links.review/marketplace -> status,
  prijs in API (from_price_usd_month) tegen JSON-LD offers.price van de reviewpagina,
  tellingen in index.json tegen de werkelijke bestanden
- MCP-verwijzingen: welke MCP-URL's en paden worden genoemd

Uitvoer: $AUDIT_OUT/07_agent_route.json + samenvatting op stdout.
"""
import collections
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from lib import AIBM_ROOT, SITES, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

idx = load_index()
FILE2REC = {r["file"]: r for recs in idx.values() for r in recs}
URLRE = re.compile(r"https?://[^\s)\]>\"'`,]+")


def status(u):
    s, f, how = url_to_file(u)
    if how == "external":
        return "extern", None
    if f is None:
        return "ONTBREEKT", None
    r = FILE2REC.get(str(f))
    if r is None:
        return "bestand (geen html)", None
    if r["refresh"]:
        return "meta-refresh", r
    if noindex(r):
        return "noindex", r
    if r["canonicals"] and norm_url(r["canonicals"][0]) != norm_url(r["url"]):
        s2, f2, h2 = url_to_file(r["canonicals"][0])
        if not (f2 and str(f2) == r["file"]):
            return "canonical-elders", r
    return "ok" + (" (fallback)" if how == "fallback" else ""), r


res = {}
# llms.txt
for site, (host, root) in SITES.items():
    for name in ("llms.txt", "llms-full.txt"):
        f = root / name
        if not f.exists():
            res[f"{site}/{name}"] = "ontbreekt"
            continue
        txt = f.read_text(errors="replace")
        urls = sorted(set(u.rstrip(".") for u in URLRE.findall(txt)))
        c = collections.Counter()
        bad = []
        for u in urls:
            st, r = status(u)
            c[st] += 1
            if st not in ("ok", "extern", "bestand (geen html)"):
                bad.append((u, st, r["canonicals"][0] if r and r["canonicals"] else None))
        langs = re.findall(r"(\d+)\s+languages", txt)
        res[f"{site}/{name}"] = {"urls": len(urls), "status": dict(c), "problemen": bad, "claims_talen": langs,
                                 "regels": txt.count("\n"), "bytes": len(txt.encode())}
        print(f"{site}/{name}: {len(urls)} URL's {dict(c)}  talen-claim: {langs}")

# API
api = AIBM_ROOT / "api" / "v1"
out = collections.defaultdict(list)
bad_json = []
prods = {}
for p in sorted(api.rglob("*.json")):
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        bad_json.append((str(p.relative_to(AIBM_ROOT)), str(e)))
        continue
    if p.parent.name == "products":
        prods[p.stem] = d
out["ongeldige_json"] = bad_json
index = json.loads((api / "index.json").read_text())
cnt = index.get("counts", {})
real = collections.Counter()
for pid, d in prods.items():
    real["products"] += 1
    real[d.get("research_status")] += 1
    if d.get("id") != pid:
        out["id_ongelijk_bestandsnaam"].append((pid, d.get("id")))
    links = d.get("links") or {}
    for k in ("review", "marketplace"):
        u = links.get(k)
        if not u:
            continue
        st, r = status(u)
        real[f"links.{k}:{st}"] += 1
        if st not in ("ok",):
            out[f"links_{k}_niet_ok"].append((pid, u, st, r["canonicals"][0] if r and r["canonicals"] else None))
    # prijsvergelijking API <-> JSON-LD van de reviewpagina
    api_p = (d.get("pricing") or {}).get("from_price_usd_month")
    u = links.get("review")
    if u and api_p is not None:
        s, f, how = url_to_file(u)
        r = FILE2REC.get(str(f)) if f else None
        # volg canonical naar de zuster: dat is de versie die Google ziet
        if r and r["canonicals"]:
            s2, f2, h2 = url_to_file(r["canonicals"][0])
            r2 = FILE2REC.get(str(f2)) if f2 else None
        else:
            r2 = None
        for label, rr in (("aibm", r), ("canonical", r2)):
            if not rr:
                continue
            prices = []
            for j in rr["jsonld"]:
                if not j["ok"]:
                    continue
                stack = [j["data"]]
                while stack:
                    o = stack.pop()
                    if isinstance(o, dict):
                        if o.get("@type") == "Offer" and o.get("price") not in (None, ""):
                            try:
                                prices.append((float(o["price"]), o.get("priceCurrency")))
                            except Exception:
                                pass
                        stack.extend(o.values())
                    elif isinstance(o, list):
                        stack.extend(o)
            usd = [p for p, c in prices if c in ("USD", None)]
            if usd and all(abs(p - float(api_p)) > 0.011 for p in usd):
                out[f"prijs_api_vs_jsonld_{label}"].append((pid, api_p, prices, rr["url"]))
    pv = (d.get("pricing") or {}).get("verified_at")
    if pv and pv > "2026-10-21":
        out["verified_at_in_toekomst"].append((pid, pv))
real_cnt = {"products": real["products"], "researched": real["researched"], "listed_not_researched": real["not_researched"]}
out["tellingen_index_vs_bestanden"] = {"index.json": {k: cnt.get(k) for k in real_cnt}, "bestanden": real_cnt}
out["link_status"] = {k: v for k, v in real.items() if k.startswith("links.")}
# openapi
oa = json.loads((api / "openapi.json").read_text())
for path in oa.get("paths", {}):
    if "{" in path:
        continue
    if not (api / path.lstrip("/")).exists():
        out["openapi_pad_zonder_bestand"].append(path)
res["api"] = out
print("\nAPI:", {k: (len(v) if isinstance(v, list) else v) for k, v in out.items()})

# MCP-verwijzingen
mcp = collections.Counter()
for site, (host, root) in SITES.items():
    for p in list(root.glob("*.html")) + list(root.glob("mcp/*.html")) + list(root.glob("agents/*.html")) + list(root.glob("llms*.txt")):
        t = p.read_text(errors="replace")
        for m in re.findall(r"https?://[\w.-]*mcp[\w./-]*|https?://[\w.-]+/mcp[\w./-]*", t):
            mcp[(site, m)] += 1
res["mcp_urls"] = [(s, u, n) for (s, u), n in mcp.most_common()]
print("\nMCP-URL's:", res["mcp_urls"][:20])
write_json("07_agent_route.json", res)
