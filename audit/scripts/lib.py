"""Gedeelde helpers voor de technische audit van 21 okt 2026.

Leest de vier sites als bestanden (geen live verkeer) en bouwt per site een
index van alle HTML-pagina's: URL, robots, canonical, titels, links, JSON-LD,
zichtbare tekst. Andere scripts in deze map laden die index via load_index().

Paden:
  AIBM      = de repo waarin dit script staat (../..)
  zusters   = $AUDIT_SISTERS (standaard: ../sisters naast deze repo)
Uitvoer   = $AUDIT_OUT (standaard: /tmp/aibm-audit-out)

Aanroep: python3 -I audit/scripts/lib.py   (bouwt de index opnieuw)
"""
import json
import os
import pickle
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

from bs4 import BeautifulSoup, Comment

HERE = Path(__file__).resolve().parent
AIBM_ROOT = HERE.parent.parent
SISTERS = Path(os.environ.get("AUDIT_SISTERS", AIBM_ROOT.parent / "sisters"))
OUT = Path(os.environ.get("AUDIT_OUT", "/tmp/aibm-audit-out"))
OUT.mkdir(parents=True, exist_ok=True)

SITES = {
    "AIBM": ("aibuildermarketplace.com", AIBM_ROOT),
    "OSM": ("officesoftwaremarketplace.com", SISTERS / "officesoftwaremarketplace"),
    "MSS": ("marketingandsalessoftware.com", SISTERS / "marketingandsalessoftware"),
    "ZTS": ("zerotouchsupport.com", SISTERS / "zerotouchsupport"),
}
HOST2SITE = {}
for k, (h, _) in SITES.items():
    HOST2SITE[h] = k
    HOST2SITE["www." + h] = k

SKIP_DIRS = {".git", "node_modules", "__pycache__", "audit"}


def site_files(site):
    host, root = SITES[site]
    for p in sorted(root.rglob("*.html")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield p, rel


def rel_to_url(site, rel):
    host = SITES[site][0]
    s = rel.as_posix()
    if s == "index.html":
        path = "/"
    elif s.endswith("/index.html"):
        path = "/" + s[: -len("index.html")]
    else:
        path = "/" + s
    return f"https://{host}{path}"


def url_to_file(url, allow_fallback=True):
    """Geeft (site, Path|None, how) voor een URL op een van de vier domeinen.

    how = 'exact'    : bestand bestaat precies zoals de URL zegt
          'fallback' : alleen via server-fallback (/x -> x.html of x/index.html)
          'missing'  : geen bestand
          'external' : geen van de vier sites
    """
    u = urlsplit(url)
    site = HOST2SITE.get((u.hostname or "").lower())
    if not site:
        return None, None, "external"
    root = SITES[site][1]
    path = unquote(u.path or "/")
    if not path.startswith("/"):
        path = "/" + path
    if path.endswith("/"):
        f = root / path.lstrip("/") / "index.html"
        return site, (f if f.is_file() else None), ("exact" if f.is_file() else "missing")
    f = root / path.lstrip("/")
    if f.is_file():
        return site, f, "exact"
    if allow_fallback:
        for cand in (root / (path.lstrip("/") + ".html"), root / path.lstrip("/") / "index.html"):
            if cand.is_file():
                return site, cand, "fallback"
    return site, None, "missing"


def norm_url(url):
    """Zonder fragment/query, host in kleine letters."""
    u = urlsplit(url)
    return f"{u.scheme}://{(u.hostname or '').lower()}{u.path or '/'}"


INVISIBLE_TAGS = ["script", "style", "noscript", "template", "svg"]


def parse_page(site, path, rel):
    raw = path.read_bytes()
    html = raw.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")
    url = rel_to_url(site, rel)
    rec = {"site": site, "file": str(path), "rel": rel.as_posix(), "url": url, "bytes": len(raw)}

    def metas(name):
        out = []
        for m in soup.find_all("meta"):
            if (m.get("name") or "").lower() == name:
                out.append((m.get("content") or "").strip())
        return out

    rec["titles"] = [t.get_text(" ", strip=True) for t in soup.find_all("title") if not t.find_parent("svg")]
    rec["descriptions"] = metas("description")
    rec["robots"] = metas("robots")
    rec["googlebot"] = metas("googlebot")
    rec["viewport"] = metas("viewport")
    rec["refresh"] = [m.get("content") for m in soup.find_all("meta") if (m.get("http-equiv") or "").lower() == "refresh"]
    rec["canonicals"] = [l.get("href", "").strip() for l in soup.find_all("link") if "canonical" in [r.lower() for r in (l.get("rel") or [])]]
    rec["hreflang"] = [(l.get("hreflang"), l.get("href")) for l in soup.find_all("link", hreflang=True)]
    htmltag = soup.find("html")
    rec["lang"] = htmltag.get("lang") if htmltag else None
    rec["h1"] = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    rec["og_url"] = [m.get("content") for m in soup.find_all("meta", property="og:url")]

    # JSON-LD
    jl = []
    for s in soup.find_all("script", type=lambda v: v and v.lower().strip() == "application/ld+json"):
        txt = s.string if s.string is not None else s.get_text()
        try:
            jl.append({"ok": True, "data": json.loads(txt), "raw": txt[:300]})
        except Exception as e:  # noqa
            jl.append({"ok": False, "error": str(e), "raw": (txt or "")[:300]})
    rec["jsonld"] = jl

    # microdata / rdfa aanwezig?
    rec["microdata"] = len(soup.find_all(attrs={"itemtype": True}))

    # scripts
    rec["scripts_ext"] = [s.get("src") for s in soup.find_all("script", src=True)]
    rec["stylesheets"] = [l.get("href") for l in soup.find_all("link") if "stylesheet" in (l.get("rel") or [])]

    # links
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "data:", "#")) or not href:
            continue
        absu = urljoin(url, href)
        if not absu.startswith("http"):
            continue
        links.append({
            "href": href,
            "abs": absu,
            "rel": [r.lower() for r in (a.get("rel") or [])],
            "text": "".join(a.find_all(string=True)).strip()[:80],
            "in_noscript": a.find_parent("noscript") is not None,
            "in_template": a.find_parent("template") is not None,
            "in_hidden": any(p.has_attr("hidden") or "display:none" in (p.get("style") or "").replace(" ", "").lower()
                             for p in a.parents if getattr(p, "attrs", None) is not None),
            "aria": a.get("aria-label"),
            "has_img": a.find("img") is not None,
        })
    rec["links"] = links

    # images
    imgs = []
    for im in soup.find_all("img"):
        imgs.append({"src": (im.get("src") or "").strip(), "alt": im.get("alt"), "loading": im.get("loading"),
                     "w": im.get("width"), "h": im.get("height")})
    rec["images"] = imgs

    # forms / buttons
    rec["inputs"] = []
    for inp in soup.find_all(["input", "select", "textarea"]):
        t = (inp.get("type") or "").lower()
        if t in ("hidden", "submit", "button", "reset", "image"):
            continue
        iid = inp.get("id")
        labelled = bool(inp.get("aria-label") or inp.get("aria-labelledby") or inp.get("title")
                        or inp.find_parent("label") or (iid and soup.find("label", attrs={"for": iid})))
        rec["inputs"].append({"tag": inp.name, "type": t, "id": iid, "name": inp.get("name"),
                              "placeholder": inp.get("placeholder"), "labelled": labelled})
    rec["buttons_noname"] = 0
    for b in soup.find_all(["button"]):
        if not (b.get_text(strip=True) or b.get("aria-label") or b.get("aria-labelledby") or b.get("title")):
            rec["buttons_noname"] += 1
    rec["links_noname"] = sum(1 for a in soup.find_all("a", href=True)
                              if not ("".join(a.find_all(string=True)).strip() or a.get("aria-label") or a.get("title")
                                      or any((im.get("alt") or "").strip() for im in a.find_all("img"))))

    # noscript inhoud
    rec["noscript_text"] = " ".join(n.get_text(" ", strip=True) for n in soup.find_all("noscript"))[:2000]

    # verborgen elementen met tekst (inline stijl / hidden-attribuut)
    hidden = []
    for el in soup.find_all(True):
        st = (el.get("style") or "").replace(" ", "").lower()
        is_hidden = (el.has_attr("hidden") or "display:none" in st or "visibility:hidden" in st
                     or ("font-size:0" in st and "font-size:0." not in st))
        if is_hidden and el.name not in ("script", "style", "template", "noscript", "svg", "input", "dialog"):
            t = el.get_text(" ", strip=True)
            if len(t) >= 40:
                hidden.append({"tag": el.name, "id": el.get("id"), "cls": " ".join(el.get("class") or []),
                               "style": (el.get("style") or "")[:80], "words": len(t.split()), "snip": t[:140]})
    rec["hidden"] = hidden

    # zichtbare tekst
    for t in soup.find_all(INVISIBLE_TAGS):
        t.decompose()
    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    body = soup.find("body")
    text = body.get_text(" ", strip=True) if body else ""
    text = re.sub(r"\s+", " ", text)
    rec["text"] = text
    rec["words"] = len(text.split())
    return rec


def build_index(sites=None):
    idx = {}
    for site in sites or SITES:
        recs = []
        for p, rel in site_files(site):
            try:
                recs.append(parse_page(site, p, rel))
            except Exception as e:  # noqa
                print("PARSE FAIL", site, rel, e, file=sys.stderr)
        idx[site] = recs
        print(site, len(recs), "pagina's", file=sys.stderr)
    with open(OUT / "index.pkl", "wb") as fh:
        pickle.dump(idx, fh)
    return idx


def load_index():
    p = OUT / "index.pkl"
    if not p.exists():
        return build_index()
    with open(p, "rb") as fh:
        return pickle.load(fh)


def by_url(idx):
    m = {}
    for site, recs in idx.items():
        for r in recs:
            m[r["url"]] = r
    return m


def noindex(rec, bot="googlebot"):
    """True als de pagina voor Google noindex is (robots of googlebot)."""
    vals = rec["robots"] + (rec["googlebot"] if bot == "googlebot" else [])
    return any("noindex" in v.lower() for v in vals)


def sitemap_urls(site, name="sitemap.xml"):
    root = SITES[site][1]
    f = root / name
    if not f.exists():
        return []
    return [u.strip() for u in re.findall(r"<loc>([^<]+)</loc>", f.read_text(errors="replace"))]


def write_json(name, data):
    with open(OUT / name, "w") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False, default=str)


if __name__ == "__main__":
    build_index()
