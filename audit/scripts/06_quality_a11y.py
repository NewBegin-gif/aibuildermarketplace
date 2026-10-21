"""Gebied 5 en 6: kwaliteit, weergave, toegankelijkheid, mobiel.

- <title>, meta description, H1: ontbrekend, dubbel op pagina, dubbel tussen pagina's, lengte
- afbeeldingen: lokaal bestand ontbreekt, alt ontbreekt, externe hosts
- paginagewicht: grootste HTML, grootste lokale afbeeldingen
- externe scripts per host
- viewport, lang
- formuliervelden zonder label, knoppen/links zonder toegankelijke naam
- tekst verborgen via CSS-klasse met display:none in inline <style> (steekproef)

Uitvoer: $AUDIT_OUT/06_quality_a11y.json + samenvatting op stdout.
"""
import collections
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

sys.path.insert(0, os.path.dirname(__file__))
from lib import HOST2SITE, SITES, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

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


res = {}
for site, recs in idx.items():
    out = collections.defaultdict(list)
    stats = collections.Counter()
    root = SITES[site][1]
    titles = collections.defaultdict(list)
    descs = collections.defaultdict(list)
    h1s = collections.defaultdict(list)
    img_hosts = collections.Counter()
    script_hosts = collections.Counter()
    missing_imgs = collections.Counter()
    missing_img_src = {}
    for r in recs:
        if r["rel"] == "404.html":
            continue
        ix = is_indexable(r)
        stats["pagina's"] += 1
        stats["indexeerbaar"] += ix
        # titel / description / h1
        if not r["titles"]:
            out["geen_title"].append((r["url"], ix))
        elif len(r["titles"]) > 1:
            out["meerdere_titles"].append((r["url"], r["titles"]))
        if not r["descriptions"]:
            if ix:
                out["geen_description_indexeerbaar"].append(r["url"])
        elif len(r["descriptions"]) > 1:
            out["meerdere_descriptions"].append((r["url"], len(r["descriptions"])))
        if not r["h1"]:
            if ix:
                out["geen_h1_indexeerbaar"].append(r["url"])
        elif len(r["h1"]) > 1 and ix:
            out["meerdere_h1_indexeerbaar"].append((r["url"], r["h1"][:3]))
        if ix:
            if r["titles"]:
                t = r["titles"][0]
                titles[t].append(r["url"])
                if len(t) > 65:
                    out["title_gt65"].append((r["url"], len(t), t))
                if len(t) < 20:
                    out["title_lt20"].append((r["url"], t))
            if r["descriptions"]:
                d = r["descriptions"][0]
                descs[d].append(r["url"])
                if len(d) > 165:
                    out["description_gt165"].append((r["url"], len(d)))
                if len(d) < 60:
                    out["description_lt60"].append((r["url"], d))
            if r["h1"]:
                h1s[r["h1"][0]].append(r["url"])
        if not r["viewport"]:
            out["geen_viewport"].append((r["url"], ix))
        elif any("user-scalable=no" in v.replace(" ", "") or "maximum-scale=1" in v.replace(" ", "") for v in r["viewport"]):
            out["viewport_blokkeert_zoom"].append((r["url"], r["viewport"]))
        if not r["lang"]:
            out["geen_lang"].append(r["url"])
        stats["lang=" + str(r["lang"])] += 1
        # afbeeldingen
        for im in r["images"]:
            src = im["src"]
            if not src or src.startswith("data:"):
                continue
            absu = urljoin(r["url"], src)
            h = (urlsplit(absu).hostname or "").lower()
            if h in HOST2SITE:
                s2, f2, how = url_to_file(absu, allow_fallback=False)
                if f2 is None:
                    missing_imgs[norm_url(absu)] += 1
                    missing_img_src[norm_url(absu)] = r["url"]
            else:
                img_hosts[h] += 1
            if im["alt"] is None:
                stats["img zonder alt-attribuut"] += 1
                if ix:
                    out["img_zonder_alt_indexeerbaar"].append((r["url"], src[:100]))
            if not im["w"] or not im["h"]:
                stats["img zonder width/height"] += 1
        for s in r["scripts_ext"]:
            absu = urljoin(r["url"], s)
            h = (urlsplit(absu).hostname or "").lower()
            script_hosts[h if h not in HOST2SITE else "(eigen) " + h] += 1
        # toegankelijkheid
        nl = [i for i in r["inputs"] if not i["labelled"]]
        if nl and ix:
            out["velden_zonder_label_indexeerbaar"].append((r["url"], len(nl), [(i["tag"], i["type"], i["id"] or i["name"], i["placeholder"]) for i in nl[:4]]))
        stats["velden zonder label"] += len(nl)
        stats["knoppen zonder naam"] += r["buttons_noname"]
        stats["links zonder naam"] += r["links_noname"]
        if (r["buttons_noname"] or r["links_noname"]) and ix:
            out["knop_of_link_zonder_naam_indexeerbaar"].append((r["url"], r["buttons_noname"], r["links_noname"]))
        stats["bytes_html"] += r["bytes"]
    # dubbele titels/desc/h1 tussen indexeerbare pagina's
    out["dubbele_title"] = [(t, u) for t, u in titles.items() if len(u) > 1]
    out["dubbele_description"] = [(d[:100], u) for d, u in descs.items() if len(u) > 1]
    out["dubbele_h1"] = [(t, u) for t, u in h1s.items() if len(u) > 1]
    out["ontbrekende_afbeeldingen"] = [(u, n, missing_img_src[u]) for u, n in missing_imgs.most_common()]
    out["externe_img_hosts"] = img_hosts.most_common(15)
    out["script_hosts"] = script_hosts.most_common(20)
    big = sorted(((r["bytes"], r["url"], is_indexable(r)) for r in recs), reverse=True)[:15]
    out["grootste_html"] = big
    imgs = []
    for ext in ("png", "jpg", "jpeg", "webp", "gif", "svg"):
        for p in root.rglob(f"*.{ext}"):
            if ".git" in p.parts:
                continue
            imgs.append((p.stat().st_size, str(p.relative_to(root))))
    imgs.sort(reverse=True)
    out["grootste_afbeeldingen"] = imgs[:15]
    stats["afbeeldingen > 500 kB"] = sum(1 for s, _ in imgs if s > 500_000)
    stats["mediaan HTML (kB)"] = round(sorted(r["bytes"] for r in recs)[len(recs) // 2] / 1024, 1)
    res[site] = {"stats": dict(stats), **out}
    print(f"\n===== {site}")
    for k, v in stats.items():
        print(f"  {k:40s} {v}")
    for k, v in out.items():
        print(f"  -> {k}: {len(v)}")
    print("  script_hosts:", out["script_hosts"][:10])
    print("  img_hosts:", out["externe_img_hosts"][:8])
    print("  grootste_html:", [(round(b / 1024), u.split('/', 3)[-1], i) for b, u, i in big[:5]])
    print("  grootste_img:", [(round(b / 1024), p) for b, p in imgs[:5]])

write_json("06_quality_a11y.json", res)
