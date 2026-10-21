"""Aanvulling gebied 1/3: sitemap-lastmod tegen dateModified/zichtbare datum,
en de videositemaps tegen VideoObject en de embed op de pagina.

Uitvoer: $AUDIT_OUT/08_sitemap_dates_video.json + samenvatting op stdout.
"""
import collections
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from lib import SITES, by_url, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

idx = load_index()
U = by_url(idx)
FILE2REC = {r["file"]: r for recs in idx.values() for r in recs}


def rec_for(u):
    s, f, how = url_to_file(u)
    return FILE2REC.get(str(f)) if f else None


def date_modified(r):
    for j in r["jsonld"]:
        d = j.get("data") if j["ok"] else None
        for it in (d if isinstance(d, list) else [d]):
            if isinstance(it, dict) and it.get("dateModified"):
                return str(it["dateModified"])[:10]
    return None


res = {}
video_ids = collections.defaultdict(list)
for site, (host, root) in SITES.items():
    out = collections.defaultdict(list)
    x = (root / "sitemap.xml").read_text(errors="replace")
    pairs = re.findall(r"<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?", x)
    lm = collections.Counter(l[:10] for _, l in pairs)
    tot = diff = vis_diff = vis_tot = 0
    for u, l in pairs:
        r = rec_for(u)
        if not r or not l:
            continue
        dm = date_modified(r)
        vis = re.findall(r"Updated (\d{4}-\d{2}-\d{2})", r["text"])
        if dm:
            tot += 1
            if dm != l[:10]:
                diff += 1
                out["lastmod_ongelijk_datemodified"].append((u, l[:10], dm, vis[:1]))
        if vis:
            vis_tot += 1
            if vis[0] != l[:10]:
                vis_diff += 1
    out["lastmod_verdeling"] = lm.most_common()
    out["telling"] = {"sitemap_urls": len(pairs), "met_dateModified": tot, "lastmod_ongelijk_dateModified": diff,
                      "met_zichtbare_Updated": vis_tot, "lastmod_ongelijk_zichtbaar": vis_diff,
                      "distinct_lastmod": len(lm), "changefreq/priority": bool(re.search(r"<(changefreq|priority)>", x))}
    # videositemap
    vf = root / "sitemap-video.xml"
    if vf.exists():
        vx = vf.read_text(errors="replace")
        for block in re.findall(r"<url>(.*?)</url>", vx, re.S):
            loc = re.search(r"<loc>([^<]+)</loc>", block).group(1)
            pl = re.search(r"<video:player_loc>([^<]+)</video:player_loc>", block)
            pd = re.search(r"<video:publication_date>([^<]+)</video:publication_date>", block)
            vid = re.search(r"(?:embed/|vi/)([\w-]{11})", block)
            vid = vid.group(1) if vid else None
            video_ids[vid].append((site, loc))
            r = rec_for(loc)
            if r is None:
                out["video_loc_ontbreekt"].append(loc)
                continue
            raw = Path(r["file"]).read_text(errors="replace")
            if vid and not re.search(r"<iframe[^>]+" + re.escape(vid), raw):
                out["video_niet_ingebed_op_pagina"].append((loc, vid))
            if noindex(r):
                out["video_pagina_noindex"].append(loc)
            if r["canonicals"] and norm_url(r["canonicals"][0]) != norm_url(r["url"]):
                out["video_pagina_canonical_elders"].append((loc, r["canonicals"][0]))
            # uploadDate in JSON-LD
            ud = None
            for j in r["jsonld"]:
                if j["ok"] and isinstance(j["data"], dict) and j["data"].get("@type") == "VideoObject":
                    ud = j["data"].get("uploadDate")
            if pd and ud and pd.group(1) != ud:
                out["publication_date_ongelijk_uploadDate"].append((loc, pd.group(1), ud))
    res[site] = out
    print(f"\n===== {site}: {out['telling']}")
    print("   lastmod-verdeling:", out["lastmod_verdeling"][:5])
    for k, v in out.items():
        if isinstance(v, list) and k not in ("lastmod_verdeling",):
            print(f"   -> {k}: {len(v)}")

# indexeerbare pagina's met VideoObject die niet in de eigen videositemap staan
for site, (host, root) in SITES.items():
    vs = set()
    vf = root / "sitemap-video.xml"
    if vf.exists():
        vs = {norm_url(u) for u in re.findall(r"<loc>([^<]+)</loc>", vf.read_text(errors="replace"))}
    miss = []
    for r in idx[site]:
        if r["rel"] == "404.html" or noindex(r) or (r["canonicals"] and norm_url(r["canonicals"][0]) != norm_url(r["url"])):
            continue
        hasv = any(j["ok"] and isinstance(j["data"], dict) and j["data"].get("@type") == "VideoObject" for j in r["jsonld"])
        if hasv and norm_url(r["url"]) not in vs:
            miss.append(r["url"])
    res[site]["indexeerbaar_met_video_niet_in_videositemap"] = miss
    print(f"{site}: indexeerbare pagina's met VideoObject die NIET in de eigen videositemap staan: {len(miss)}")

dups = {v: locs for v, locs in video_ids.items() if v and len(locs) > 1}
res["zelfde_video_in_meerdere_videositemaps"] = dups
print("\nzelfde YouTube-ID in >1 videositemap-item:", len(dups), list(dups.items())[:3])
write_json("08_sitemap_dates_video.json", res)
