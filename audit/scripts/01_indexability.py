"""Gebied 1: indexeerbaarheid (robots, canonical, sitemaps, hreflang).

Uitvoer: $AUDIT_OUT/01_indexability.json + samenvatting op stdout.
"""
import collections
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import (SITES, by_url, load_index, noindex, norm_url, sitemap_urls,  # noqa: E402
                 url_to_file, write_json)

idx = load_index()
U = by_url(idx)
res = {}


def page_for(url):
    """Pagina-record voor een URL, met server-fallback."""
    site, f, how = url_to_file(url)
    if how in ("exact", "fallback"):
        for r in idx[site]:
            if r["file"] == str(f):
                return r, how
    return None, how


def classify(rec):
    c = rec["canonicals"]
    if not c:
        return "geen"
    if len(set(c)) > 1:
        return "meerdere"
    tgt = norm_url(c[0])
    if tgt == norm_url(rec["url"]):
        return "zelf"
    # zelf via .html-loze variant?
    site, f, how = url_to_file(tgt)
    if site == rec["site"] and f and str(f) == rec["file"]:
        return "zelf-variant"
    if site and site != rec["site"]:
        return "zuster"
    if site == rec["site"]:
        return "elders-zelfde-site"
    return "extern"


for site in SITES:
    recs = idx[site]
    out = collections.defaultdict(list)
    sm = sitemap_urls(site)
    smv = sitemap_urls(site, "sitemap-video.xml")
    smr = sitemap_urls(site, "sitemap-verwijderd.xml")
    smset = set(norm_url(u) for u in sm)
    stats = collections.Counter()

    for r in recs:
        if r["rel"] in ("404.html",):
            continue
        ni_all = any("noindex" in v.lower() for v in r["robots"])
        ni_g = any("noindex" in v.lower() for v in r["googlebot"])
        r_cls = classify(r)
        stats["pagina's"] += 1
        stats["noindex (robots)"] += ni_all
        stats["noindex (alleen googlebot)"] += (ni_g and not ni_all)
        stats["canonical:" + r_cls] += 1
        if len(r["robots"]) > 1:
            out["meerdere_meta_robots"].append((r["url"], r["robots"]))
        if r["refresh"]:
            out["meta_refresh"].append((r["url"], r["refresh"], r["canonicals"]))
        if r_cls == "meerdere":
            out["meerdere_canonicals"].append((r["url"], r["canonicals"]))
        if r_cls == "zelf-variant":
            out["canonical_variant"].append((r["url"], r["canonicals"][0]))
        if r_cls == "geen" and not noindex(r) and not r["refresh"]:
            out["geen_canonical_indexeerbaar"].append(r["url"])
        if r["canonicals"] and not r["canonicals"][0].startswith("http"):
            out["canonical_relatief"].append((r["url"], r["canonicals"][0]))
        # noindex + canonical elders: tegenstrijdige signalen
        if noindex(r) and r_cls in ("zuster", "elders-zelfde-site"):
            out["noindex_en_canonical_elders"].append((r["url"], r["canonicals"][0], r["robots"] + r["googlebot"]))
        # canonical doel controleren
        if r_cls in ("zuster", "elders-zelfde-site", "zelf-variant"):
            tgt = r["canonicals"][0]
            t, how = page_for(tgt)
            if t is None:
                out["canonical_naar_ontbrekend"].append((r["url"], tgt))
            else:
                if how == "fallback" and r_cls != "zelf-variant":
                    out["canonical_naar_fallback_url"].append((r["url"], tgt, t["url"]))
                if noindex(t):
                    out["canonical_naar_noindex"].append((r["url"], tgt, t["robots"] + t["googlebot"]))
                tc = classify(t)
                if tc in ("zuster", "elders-zelfde-site"):
                    out["canonical_keten"].append((r["url"], tgt, t["canonicals"][0]))
                if t["refresh"]:
                    out["canonical_naar_refresh"].append((r["url"], tgt, t["refresh"]))
        # og:url vs canonical
        if r["og_url"] and r["canonicals"] and norm_url(r["og_url"][0]) != norm_url(r["canonicals"][0]):
            out["og_url_wijkt_af"].append((r["url"], r["og_url"][0], r["canonicals"][0]))
        # sitemap-relaties
        in_sm = norm_url(r["url"]) in smset or (r["canonicals"] and norm_url(r["canonicals"][0]) in smset and r_cls in ("zelf", "zelf-variant"))
        if not in_sm and not noindex(r) and r_cls in ("zelf", "zelf-variant") and not r["refresh"]:
            out["indexeerbaar_niet_in_sitemap"].append(r["url"])
        if r["hreflang"]:
            stats["met hreflang"] += 1

    # sitemap-inhoud controleren
    for u in sm:
        t, how = page_for(u)
        if t is None:
            out["sitemap_naar_ontbrekend"].append(u)
            continue
        if how == "fallback":
            out["sitemap_fallback_url"].append((u, t["url"]))
        if noindex(t):
            out["sitemap_bevat_noindex"].append((u, t["robots"] + t["googlebot"]))
        cl = classify(t)
        if cl in ("zuster", "elders-zelfde-site"):
            out["sitemap_bevat_canonical_elders"].append((u, t["canonicals"][0]))
        if t["refresh"]:
            out["sitemap_bevat_refresh"].append((u, t["refresh"]))
        if cl == "zelf-variant" and norm_url(u) != norm_url(t["canonicals"][0]):
            out["sitemap_url_ongelijk_canonical"].append((u, t["canonicals"][0]))
    dup = [u for u, n in collections.Counter(norm_url(x) for x in sm).items() if n > 1]
    out["sitemap_dubbel"] = dup
    for u in smv:
        t, how = page_for(u)
        if t is None:
            out["videositemap_naar_ontbrekend"].append(u)
        elif noindex(t):
            out["videositemap_bevat_noindex"].append((u, t["robots"] + t["googlebot"]))
        elif classify(t) in ("zuster", "elders-zelfde-site"):
            out["videositemap_bevat_canonical_elders"].append((u, t["canonicals"][0]))
    for u in smr:
        t, how = page_for(u)
        if t is not None:
            out["verwijderd_maar_bestaat"].append((u, how, "noindex" if noindex(t) else "INDEXEERBAAR", classify(t)))
    stats["sitemap.xml URL's"] = len(sm)
    stats["sitemap-video URL's"] = len(smv)
    stats["sitemap-verwijderd URL's"] = len(smr)
    res[site] = {"stats": dict(stats), **{k: v for k, v in out.items()}}

    print(f"\n===== {site}")
    for k, v in sorted(stats.items()):
        print(f"  {k:40s} {v}")
    for k, v in out.items():
        print(f"  -> {k}: {len(v)}")

write_json("01_indexability.json", res)
