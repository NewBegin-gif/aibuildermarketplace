"""Gebied 2: interne links, wezen, linkdiepte, links tussen de vier sites,
en (gebied 4) affiliatelinks zonder rel="sponsored"/"nofollow".

Uitvoer: $AUDIT_OUT/02_links.json + samenvatting op stdout.
"""
import collections
import re
import sys
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import HOST2SITE, SITES, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

idx = load_index()
FILE2REC = {r["file"]: r for recs in idx.values() for r in recs}
ASSET_EXT = re.compile(r"\.(png|jpe?g|webp|gif|svg|pdf|xml|json|txt|css|js|ico|mp4|webm|csv|zip|md)$", re.I)

AFF_HOST = re.compile(r"(^|\.)(awin1\.com|shoffi\.app|kqzyfj\.com|tkqlhce\.com|anrdoezrs\.net|jdoqocy\.com|dpbolvw\.net|"
                      r"partnerstack\.com|impact\.com|sjv\.io|pxf\.io|go2cloud\.org|linksynergy\.com|shareasale\.com|"
                      r"pntra\.com|pjtra\.com|tradedoubler\.com|digistore24\.com|fmtrk\.com)$", re.I)
AFF_SUB = re.compile(r"^(try|get|join|refer|referral|affiliate|affiliates|aff|partners?|partnersps|go|start|now)\.", re.I)
AFF_PARAMS = {"aff", "ref", "via", "fpr", "referral", "referralcode", "awinaffid", "affiliate", "aff_id",
              "affid", "partner", "utm_affiliate_network", "irclickid", "red", "gr_pk", "kaid", "atp"}


def is_affiliate(u):
    p = urlsplit(u)
    h = (p.hostname or "").lower()
    if AFF_HOST.search(h):
        return "netwerk"
    keys = {k.lower() for k in parse_qs(p.query)}
    if keys & AFF_PARAMS:
        return "param:" + ",".join(sorted(keys & AFF_PARAMS))
    if AFF_SUB.match(h):
        return "subdomein"
    return None


def cls_canon(r):
    if not r["canonicals"]:
        return "geen"
    t = norm_url(r["canonicals"][0])
    if t == norm_url(r["url"]):
        return "zelf"
    s, f, h = url_to_file(t)
    if s == r["site"] and f and str(f) == r["file"]:
        return "zelf"
    return "elders"


res = {}
for site in SITES:
    recs = idx[site]
    inbound = collections.defaultdict(set)      # doelbestand -> set(bronurl)
    inbound_idx = collections.defaultdict(set)  # alleen vanaf indexeerbare bronnen
    graph = collections.defaultdict(set)
    graph_dom = collections.defaultdict(set)    # zonder links die alleen in <template> staan
    inbound_dom = collections.defaultdict(set)
    out = collections.defaultdict(list)
    broken = collections.Counter()
    broken_src = collections.defaultdict(set)
    to_noindex = collections.Counter()
    to_canon_elsewhere = collections.Counter()
    to_refresh = collections.Counter()
    to_fallback = collections.Counter()
    cross = collections.Counter()
    cross_rel = collections.Counter()
    aff_bad = []
    aff_total = 0
    stats = collections.Counter()

    for r in recs:
        if r["rel"] == "404.html":
            continue
        src_indexable = not noindex(r) and cls_canon(r) == "zelf"
        for l in r["links"]:
            u = urlsplit(l["abs"])
            host = (u.hostname or "").lower()
            tsite = HOST2SITE.get(host)
            if tsite == site:
                if ASSET_EXT.search(u.path) and not u.path.endswith(".html"):
                    continue
                stats["interne links"] += 1
                s, f, how = url_to_file(l["abs"])
                if f is None:
                    broken[norm_url(l["abs"])] += 1
                    broken_src[norm_url(l["abs"])].add(r["url"])
                    continue
                if how == "fallback":
                    to_fallback[norm_url(l["abs"])] += 1
                t = FILE2REC.get(str(f))
                if t is None:
                    continue
                if t["file"] != r["file"]:
                    inbound[t["file"]].add(r["url"])
                    if src_indexable:
                        inbound_idx[t["file"]].add(r["url"])
                    graph[r["file"]].add(t["file"])
                    if not l["in_template"]:
                        graph_dom[r["file"]].add(t["file"])
                        inbound_dom[t["file"]].add(r["url"])
                if noindex(t):
                    to_noindex[t["url"]] += 1
                if cls_canon(t) == "elders":
                    to_canon_elsewhere[t["url"]] += 1
                if t["refresh"]:
                    to_refresh[t["url"]] += 1
            elif tsite:
                cross[tsite] += 1
                cross_rel[(tsite, " ".join(sorted(l["rel"])) or "(geen)")] += 1
                s, f, how = url_to_file(l["abs"])
                if f is None and not ASSET_EXT.search(u.path):
                    out["kruislink_gebroken"].append((r["url"], l["abs"]))
            else:
                a = is_affiliate(l["abs"])
                if a:
                    aff_total += 1
                    if not ({"sponsored", "nofollow"} & set(l["rel"])):
                        aff_bad.append((r["url"], l["abs"][:140], l["rel"], a))

    # wezen en diepte
    home = str(SITES[site][1] / "index.html")
    depth = {home: 0}
    q = collections.deque([home])
    while q:
        cur = q.popleft()
        for n in graph.get(cur, ()):
            if n not in depth:
                depth[n] = depth[cur] + 1
                q.append(n)
    indexable = [r for r in recs if r["rel"] != "404.html" and not noindex(r) and cls_canon(r) == "zelf" and not r["refresh"]]
    for r in indexable:
        if r["file"] == home:
            continue
        if not inbound.get(r["file"]):
            out["wees_geen_enkele_link"].append(r["url"])
        elif not inbound_idx.get(r["file"]):
            out["wees_alleen_links_vanaf_noindex"].append((r["url"], sorted(inbound[r["file"]])[:3]))
        d = depth.get(r["file"])
        if d is None:
            out["onbereikbaar_vanaf_home"].append(r["url"])
        elif d > 3:
            out["diepte_gt3"].append((r["url"], d))
    dd = collections.Counter(depth.get(r["file"], "onbereikbaar") for r in indexable)
    # zelfde berekening zonder <template>-links (die staan niet in de DOM zolang JS ze niet invoegt)
    depth2 = {home: 0}
    q = collections.deque([home])
    while q:
        cur = q.popleft()
        for n in graph_dom.get(cur, ()):
            if n not in depth2:
                depth2[n] = depth2[cur] + 1
                q.append(n)
    out["diepteverdeling_zonder_template"] = sorted(collections.Counter(depth2.get(r["file"], "onbereikbaar") for r in indexable).items(), key=lambda x: str(x[0]))
    out["alleen_via_template_bereikbaar_of_dieper"] = sorted(
        (r["url"], depth.get(r["file"]), depth2.get(r["file"])) for r in indexable
        if r["file"] != home and depth2.get(r["file"], 99) > depth.get(r["file"], 99))
    out["wees_zonder_template"] = sorted(r["url"] for r in indexable if r["file"] != home and not inbound_dom.get(r["file"]))
    stats["indexeerbare pagina's"] = len(indexable)
    out["diepteverdeling_indexeerbaar"] = sorted(dd.items(), key=lambda x: str(x[0]))
    out["gebroken_intern"] = sorted(((u, n, sorted(broken_src[u])[:3]) for u, n in broken.items()), key=lambda x: -x[1])
    out["links_naar_noindex"] = to_noindex.most_common()
    out["links_naar_canonical_elders"] = to_canon_elsewhere.most_common()
    out["links_naar_meta_refresh"] = to_refresh.most_common()
    out["links_via_fallback"] = to_fallback.most_common()
    out["kruislinks"] = dict(cross)
    out["kruislinks_rel"] = [(k[0], k[1], v) for k, v in cross_rel.most_common()]
    out["affiliate_zonder_sponsored_nofollow"] = aff_bad
    stats["affiliatelinks (heuristiek)"] = aff_total
    stats["gebroken interne link-doelen"] = len(broken)
    stats["gebroken interne link-verwijzingen"] = sum(broken.values())
    res[site] = {"stats": dict(stats), **out}
    print(f"\n===== {site}")
    for k, v in stats.items():
        print(f"  {k:40s} {v}")
    for k, v in out.items():
        print(f"  -> {k}: {len(v)}")
    print("  diepte:", out["diepteverdeling_indexeerbaar"])
    print("  diepte zonder <template>-links:", out["diepteverdeling_zonder_template"])
    print("  kruislinks rel:", out["kruislinks_rel"][:12])

write_json("02_links.json", res)
