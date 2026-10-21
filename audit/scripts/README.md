# Scripts technische audit 21 okt 2026

Alleen lezen: geen script wijzigt de sites. Alles werkt op de repo-inhoud; live verkeer naar de vier domeinen was in de auditomgeving geblokkeerd.

## Opzet

```
<werkmap>/aibuildermarketplace                 # deze repo (branch main)
<werkmap>/sisters/officesoftwaremarketplace    # git clone --depth 1
<werkmap>/sisters/marketingandsalessoftware
<werkmap>/sisters/zerotouchsupport
```

Omgevingsvariabelen (optioneel):

- `AUDIT_SISTERS`: map met de drie zuster-repo's (standaard `../sisters` naast deze repo)
- `AUDIT_OUT`: uitvoermap voor index en JSON-resultaten (standaard `/tmp/aibm-audit-out`)

Vereist: Python 3.11+ met `beautifulsoup4` en `lxml`. Voor 09/11: Node 18+ met `playwright` (Chromium) en, voor 11, `axe-core` 4.10.

## Volgorde

| Script | Gebied | Wat het doet |
|---|---|---|
| `lib.py` | basis | Parseert alle HTML van de vier sites naar `$AUDIT_OUT/index.pkl` (draai eerst, en opnieuw na elke wijziging) |
| `01_indexability.py` | 1 | robots/googlebot, canonical (zelf, zuster, ketens, naar noindex/ontbrekend), sitemaps, videositemaps, sitemap-verwijderd, og:url |
| `02_links.py` | 2, 4 | interne links (gebroken, naar noindex/canonical-elders), wezen, linkdiepte (ook zonder `<template>`-links), kruislinks + rel, affiliatelinks zonder sponsored/nofollow |
| `03_structured_data.py` | 3 | JSON-LD: geldigheid, verplichte velden, dubbele blokken, prijs/datum/auteur/FAQ tegen zichtbare tekst, VideoObject zonder embed, breadcrumbs |
| `04_similarity.py` | 4 | 5-shingles zonder sjabloon: paren binnen sites, tussen sites, AIBM-kopie vs zuster (`SIM_THRESH`, standaard 0.30) |
| `05_template_sentences.py` | 4 | sjabloonzinnen in reviews, dezelfde slug op meerdere domeinen |
| `06_quality_a11y.py` | 5, 6 | title/description/H1, afbeeldingen, paginagewicht, externe scripts, viewport, labels, namen |
| `07_agent_route.py` | 7 | llms.txt-URL's, `/api/v1/` (geldigheid, links, prijs API vs JSON-LD, tellingen, OpenAPI), MCP-URL's |
| `08_sitemap_dates_video.py` | 1, 3 | sitemap-lastmod vs dateModified/zichtbare datum, videositemap vs embed/VideoObject |
| `09_render_prep.py` + `09_render.cjs` + `09_render_analyse.py` | 4, 5, 6 | Chromium-weergave met en zonder JS (offline, verzoeken uit de lokale repo's), verschillen, JS-fouten, overloop op 412 px |
| `10_heading_skeleton.py` | 4 | H2-skelet van indexeerbare reviews per site en over de vier sites |
| `11_axe.cjs` | 6 | axe-core-steekproef (17 pagina's): contrast, labels, namen, alt, lang, viewport |

Voorbeeld:

```bash
export AUDIT_SISTERS=../sisters AUDIT_OUT=/tmp/aibm-audit-out
python3 -I audit/scripts/lib.py
for s in 01_indexability 02_links 03_structured_data 04_similarity 05_template_sentences \
         06_quality_a11y 07_agent_route 08_sitemap_dates_video 10_heading_skeleton; do
  python3 -I audit/scripts/$s.py
done
python3 -I audit/scripts/09_render_prep.py
NODE_PATH=$(npm root -g) node audit/scripts/09_render.cjs $AUDIT_OUT/render_urls.txt $AUDIT_OUT/render.json
python3 -I audit/scripts/09_render_analyse.py
AXE=/pad/naar/node_modules/axe-core/axe.min.js NODE_PATH=$(npm root -g) node audit/scripts/11_axe.cjs $AUDIT_OUT/11_axe.json
```

## Beperkingen

- Geen HTTP-statuscodes: 301/410 op de server (Caddy) zijn niet in de repo te zien. Een "bestand ontbreekt" kan live een redirect zijn.
- URL's zonder `.html` worden opgelost zoals GitHub Pages/Caddy gewoonlijk doen (`/x` -> `x.html` of `x/index.html`).
- Affiliatelinks worden heuristisch herkend (netwerkdomeinen, ref-parameters, subdomeinen als `try.`/`get.`).
