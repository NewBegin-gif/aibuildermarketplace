"""Gebied 3: structured data (JSON-LD).

- geldigheid van de JSON
- verplichte/aanbevolen velden voor de rich-result-typen van Google
- dubbele blokken per pagina
- tegenstrijdigheden met de zichtbare tekst (prijs, datum, auteur, FAQ-vragen)
- VideoObject zonder bijbehorende embed op de pagina
- breadcrumbs/urls in JSON-LD die afwijken van de canonical

Uitvoer: $AUDIT_OUT/03_structured_data.json + samenvatting op stdout.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import SITES, load_index, noindex, norm_url, url_to_file, write_json  # noqa: E402

idx = load_index()
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")


def walk(o, parent=None):
    if isinstance(o, dict):
        t = o.get("@type")
        if t:
            yield (t if isinstance(t, str) else "|".join(t)), o, parent
        for k, v in o.items():
            yield from walk(v, o if t else parent)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, parent)


def g(o, *keys):
    for k in keys:
        if isinstance(o, list):
            o = o[0] if o else None
        if not isinstance(o, dict):
            return None
        o = o.get(k)
    return o


def as_list(x):
    return x if isinstance(x, list) else ([] if x is None else [x])


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None


def price_variants(p):
    """Tekstvormen waarin een prijs zichtbaar kan staan."""
    out = set()
    if p is None:
        return out
    if p == int(p):
        out |= {f"{int(p)}", f"{int(p):,}", f"{p:.2f}"}
    else:
        out |= {f"{p:.2f}", f"{p:g}", f"{p:.2f}".replace(".", ",")}
    return out


res = {}
for site in SITES:
    out = collections.defaultdict(list)
    stats = collections.Counter()
    for r in idx[site]:
        if r["rel"] == "404.html":
            continue
        indexable = not noindex(r) and (not r["canonicals"] or norm_url(r["canonicals"][0]) == norm_url(r["url"]))
        raw = None
        types_top = collections.Counter()
        for j in r["jsonld"]:
            stats["blokken"] += 1
            if not j["ok"]:
                out["ongeldige_json"].append((r["url"], j["error"], j["raw"][:120]))
                continue
            d = j["data"]
            for it in as_list(d):
                if isinstance(it, dict):
                    if "@graph" in it:
                        for gi in it["@graph"]:
                            types_top[str(gi.get("@type"))] += 1
                    else:
                        types_top[str(it.get("@type"))] += 1
                    ctx = it.get("@context")
                    if ctx and "schema.org" not in str(ctx):
                        out["vreemde_context"].append((r["url"], ctx))
            for t, o, parent in walk(d):
                stats["type:" + t] += 1
                if t in ("SoftwareApplication", "WebApplication", "Product"):
                    offers = as_list(o.get("offers"))
                    has_rating = bool(o.get("aggregateRating")) or any(g(rv, "reviewRating", "ratingValue") is not None for rv in as_list(o.get("review")))
                    if not offers:
                        out[f"{t}_zonder_offers"].append(r["url"])
                    if not has_rating:
                        stats[f"{t} zonder rating (niet rich-result-geschikt)"] += 1
                    for of in offers:
                        p = of.get("price") if isinstance(of, dict) else None
                        if isinstance(of, dict) and of.get("@type") == "AggregateOffer":
                            p = of.get("lowPrice")
                        if p is None:
                            out["offer_zonder_price"].append((r["url"], str(of)[:120]))
                        elif num(p) is None:
                            out["offer_price_niet_numeriek"].append((r["url"], p))
                        if isinstance(of, dict) and not of.get("priceCurrency"):
                            out["offer_zonder_currency"].append((r["url"], p))
                        # prijs zichtbaar op de pagina?
                        pv = num(p)
                        if pv is not None and pv > 0:
                            vs = price_variants(pv)
                            if not any(re.search(r"(?<![\d.,])" + re.escape(v) + r"(?![\d])", r["text"]) for v in vs):
                                out["offer_prijs_niet_zichtbaar"].append((r["url"], o.get("name"), p, of.get("priceCurrency") if isinstance(of, dict) else None))
                    u = o.get("url")
                    if u and r["canonicals"] and norm_url(u) != norm_url(r["canonicals"][0]):
                        out["app_url_ongelijk_canonical"].append((r["url"], u, r["canonicals"][0]))
                if t == "Review":
                    if not o.get("author"):
                        out["review_zonder_author"].append(r["url"])
                    if not g(o, "reviewRating", "ratingValue"):
                        stats["Review zonder reviewRating"] += 1
                    ir = o.get("itemReviewed")
                    if parent is None and not ir:
                        out["review_zonder_itemReviewed"].append(r["url"])
                    irn = str(g(o, "itemReviewed", "name") or "")
                    if irn and re.search(r"aibuilder|office software|marketing and sales|zero ?touch", irn, re.I):
                        out["review_self_serving"].append((r["url"], irn))
                if t == "AggregateRating":
                    out["aggregaterating"].append((r["url"], o.get("ratingValue"), o.get("ratingCount") or o.get("reviewCount"), parent and parent.get("@type")))
                if t == "VideoObject":
                    miss = [k for k in ("name", "thumbnailUrl", "uploadDate") if not o.get(k)]
                    if miss:
                        out["video_mist_verplicht"].append((r["url"], miss))
                    if not o.get("description"):
                        stats["VideoObject zonder description"] += 1
                    ud = o.get("uploadDate")
                    if ud and not ISO.match(str(ud)):
                        out["video_uploaddate_niet_iso"].append((r["url"], ud))
                    if ud and re.match(r"^\d{4}-\d{2}-\d{2}T", str(ud)) is None:
                        stats["uploadDate zonder tijd/tijdzone"] += 1
                    if not (o.get("contentUrl") or o.get("embedUrl")):
                        out["video_zonder_content_of_embed"].append(r["url"])
                    vid = None
                    for k in ("embedUrl", "contentUrl", "thumbnailUrl"):
                        m = re.search(r"(?:embed/|vi/|v=|youtu\.be/|shorts/)([\w-]{11})", str(o.get(k) or ""))
                        if m:
                            vid = m.group(1)
                            break
                    if raw is None:
                        raw = Path(r["file"]).read_text(errors="replace")
                    if vid and raw.count(vid) < 2:
                        out["video_id_niet_op_pagina"].append((r["url"], vid))
                    if vid and not re.search(r"<iframe[^>]+" + re.escape(vid) + r"|data-(?:id|video|yt|src)[^>]*" + re.escape(vid) + r"|lite-youtube[^>]+" + re.escape(vid), raw):
                        out["video_geen_embed_element"].append((r["url"], vid))
                    thumbs = re.findall(r"vi/([\w-]{11})/", str(o.get("thumbnailUrl")))
                    emb = re.findall(r"embed/([\w-]{11})", str(o.get("embedUrl")))
                    if thumbs and emb and thumbs[0] != emb[0]:
                        out["video_thumb_embed_ongelijk"].append((r["url"], thumbs[0], emb[0]))
                    clips = as_list(o.get("hasPart"))
                    offs = []
                    for c in clips:
                        if not isinstance(c, dict):
                            continue
                        miss = [k for k in ("name", "startOffset", "url") if c.get(k) in (None, "")]
                        if miss:
                            out["clip_mist_verplicht"].append((r["url"], miss))
                        so = num(c.get("startOffset"))
                        eo = num(c.get("endOffset"))
                        offs.append(so)
                        if so is not None and eo is not None and eo <= so:
                            out["clip_endoffset_le_start"].append((r["url"], so, eo))
                        cu = str(c.get("url") or "")
                        if cu and "t=" not in cu and "#" not in cu:
                            out["clip_url_zonder_tijd"].append((r["url"], cu))
                    if offs and any(a is not None and b is not None and b < a for a, b in zip(offs, offs[1:])):
                        out["clip_offsets_niet_oplopend"].append(r["url"])
                    if len(offs) != len(set(offs)) and offs:
                        out["clip_dubbele_offsets"].append(r["url"])
                if t == "FAQPage":
                    qs = as_list(o.get("mainEntity"))
                    if not qs:
                        out["faq_zonder_vragen"].append(r["url"])
                    notvis = 0
                    for q in qs:
                        if not isinstance(q, dict):
                            continue
                        qn = (q.get("name") or "").strip()
                        at = g(q, "acceptedAnswer", "text")
                        if not qn or not at:
                            out["faq_vraag_of_antwoord_leeg"].append((r["url"], qn[:60]))
                        key = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", qn))[:50]
                        if key and key not in r["text"]:
                            notvis += 1
                    if notvis:
                        out["faq_vraag_niet_zichtbaar"].append((r["url"], notvis, len(qs)))
                if t == "BreadcrumbList":
                    items = as_list(o.get("itemListElement"))
                    pos = [num(i.get("position")) for i in items if isinstance(i, dict)]
                    if pos != list(range(1, len(pos) + 1)):
                        out["breadcrumb_posities_fout"].append((r["url"], pos))
                    for n, it in enumerate(items):
                        if not isinstance(it, dict):
                            continue
                        item = it.get("item")
                        iu = item.get("@id") if isinstance(item, dict) else item
                        if not it.get("name") and not (isinstance(item, dict) and item.get("name")):
                            out["breadcrumb_zonder_name"].append(r["url"])
                        if iu:
                            s2, f2, how = url_to_file(iu)
                            if how == "missing":
                                out["breadcrumb_naar_ontbrekend"].append((r["url"], iu))
                            elif how == "external":
                                out["breadcrumb_extern"].append((r["url"], iu))
                            elif s2 != site:
                                out["breadcrumb_naar_andere_site"].append((r["url"], iu))
                        elif n < len(items) - 1:
                            out["breadcrumb_tussenitem_zonder_item"].append(r["url"])
                    if items and r["canonicals"]:
                        last = items[-1].get("item") if isinstance(items[-1], dict) else None
                        last = last.get("@id") if isinstance(last, dict) else last
                        if last and norm_url(last) != norm_url(r["canonicals"][0]) and norm_url(last) != norm_url(r["url"]):
                            out["breadcrumb_laatste_ongelijk_pagina"].append((r["url"], last, r["canonicals"][0]))
                if t == "Article":
                    if not o.get("headline"):
                        out["article_zonder_headline"].append(r["url"])
                    elif len(o["headline"]) > 110:
                        stats["Article headline >110 tekens"] += 1
                    an = str(g(o, "author", "name") or "")
                    if not an:
                        out["article_zonder_author"].append(r["url"])
                    elif an not in r["text"]:
                        out["auteursnaam_niet_zichtbaar"].append((r["url"], an))
                    dm = str(o.get("dateModified") or "")[:10]
                    if dm:
                        vis = re.findall(r"Updated (\d{4}-\d{2}-\d{2})", r["text"])
                        if vis and dm not in vis:
                            out["datemodified_ongelijk_zichtbaar"].append((r["url"], dm, vis[:2]))
                    dp = str(o.get("datePublished") or "")[:10]
                    if dp and dm and dm < dp:
                        out["datemodified_voor_datepublished"].append((r["url"], dp, dm))
                    if dm and dm > "2026-10-21":
                        out["datum_in_toekomst"].append((r["url"], dm))
                if t == "HowTo":
                    stats["HowTo (geen rich result meer sinds 2023)"] += 1
        for t, n in types_top.items():
            if n > 1 and t not in ("ListItem", "Question"):
                out["dubbel_type_op_pagina"].append((r["url"], t, n))
        if indexable:
            stats["indexeerbare pagina's met JSON-LD"] += bool(r["jsonld"])
    res[site] = {"stats": dict(stats), **out}
    print(f"\n===== {site}")
    for k, v in sorted(stats.items()):
        print(f"  {k:55s} {v}")
    for k, v in out.items():
        print(f"  -> {k}: {len(v)}")

write_json("03_structured_data.json", res)
