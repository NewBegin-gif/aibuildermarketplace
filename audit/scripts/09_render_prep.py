"""Maakt de URL-lijst voor 09_render.cjs: alle indexeerbare pagina's van de vier
sites, plus de googlebot-noindex-reviews en een steekproef AIBM-kopieen.

Uitvoer: $AUDIT_OUT/render_urls.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import OUT, load_index, noindex, norm_url, url_to_file  # noqa: E402

idx = load_index()
urls = []
for site, recs in idx.items():
    for r in recs:
        if r["rel"] == "404.html" or r["refresh"]:
            continue
        canon_self = not r["canonicals"] or norm_url(r["canonicals"][0]) == norm_url(r["url"])
        if not noindex(r) and canon_self:
            urls.append(r["url"])
        elif site == "AIBM" and any("noindex" in v for v in r["googlebot"]):
            urls.append(r["url"])
copies = [r["url"] for r in idx["AIBM"] if r["canonicals"] and url_to_file(r["canonicals"][0])[0] not in (None, "AIBM")]
urls += copies[::13]
(OUT / "render_urls.txt").write_text("\n".join(urls) + "\n")
print(len(urls), "URL's ->", OUT / "render_urls.txt")
