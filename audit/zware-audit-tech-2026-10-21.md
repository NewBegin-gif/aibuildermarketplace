# Zware technische audit AIBM + drie zustersites (21 okt 2026)

Scope: aibuildermarketplace.com (AIBM, deze repo, `main` @ `90eaea3c`), officesoftwaremarketplace.com (OSM @ `785caac`), marketingandsalessoftware.com (MSS @ `ad43be1`), zerotouchsupport.com (ZTS @ `f2b1a21`). Alle vier repo's zijn op 21 okt 2026 gelezen; de zusters als `git clone --depth 1`.

**Belangrijke beperking: alles hieronder is gemeten op de repo-inhoud, niet live.** De auditomgeving weigerde verbindingen met de vier domeinen (proxy: `connect_rejected`). Daardoor zijn HTTP-statuscodes, server-redirects (Caddy) en response-headers niet gezien. Waar een bevinding daarvan afhangt, staat dat erbij en is ze PLAUSIBLE. Weergave met JavaScript is offline nagebootst in Chromium, met de vier domeinen uit de lokale bestanden (script 09).

Alle checks zijn herhaalbaar met de scripts in `audit/scripts/` (zie de README daar). Elke telling in dit rapport komt uit een van die scripts; het scriptnummer staat bij de bevinding.

---

## Samenvatting

### Top-10 op impact voor herstel in Google

| # | Code | Site | Ernst | In één zin |
|---|---|---|---|---|
| 1 | T21-01 | AIBM | hoog | 327 indexeerbare AIBM-reviews hebben een canonical naar een zuster, maar zijn geen duplicaat: ze bevatten mediaan 987 woorden tegenover 2.881 op de zuster (Jaccard < 0,5). Google mag zo'n canonical negeren, en dan staan er honderden ingekorte kopieën in de index. |
| 2 | T21-22 | alle | midden | Het viervoudige netwerk is technisch goed te herkennen: 535 van de 536 indexeerbare reviews over vier domeinen hebben dezelfde vijf H2's, en 12 paden (o.a. `tools/renewal-check`, `mcp`, `atlas`, `finder`) zijn op 2 tot 4 domeinen tegelijk indexeerbaar. |
| 3 | T21-23 | alle | midden | Sinds 20 okt staat op 560 reviews een blok met placeholdertekst ("Being verified … not yet matched to a line on the vendor's own pages"). Die tekst is identiek en verscheen midden in de herstelperiode. |
| 4 | T21-03 | alle | midden | De sitemap-lastmod klopt bij 89–93% van de URL's niet met de dateModified en de zichtbare "Updated"-datum. Lastmod volgt sjabloon-rebuilds en niet echte inhoudswijzigingen. |
| 5 | T21-10 | ZTS | midden | Drie oude dunne artikelen (800.html, pylon.html, surveysparrow.html, 500–660 woorden) staan nog indexeerbaar in de sitemap, naast de echte reviews van dezelfde producten. |
| 6 | T21-04, T21-15 | alle | midden | De videosignalen spreken elkaar tegen. AIBM meldt 43 video-URL's die noindex zijn of een canonical elders hebben, en 298 AIBM-kopieën hebben VideoObject-markup zonder video. 97 zusterpagina's mét video staan niet in hun eigen videositemap. |
| 7 | T21-02 | AIBM | midden | sitemap.xml bevat 5 `/build/`-pagina's die met een canonical naar een zuster wijzen. |
| 8 | T21-11 | AIBM | midden | AIBM linkt intern 5.275 keer naar 1.256 noindex-pagina's en 5.549 keer naar 381 eigen kopieën met canonical elders. Daardoor gaat de meeste interne linkwaarde naar pagina's die niet in de index horen. |
| 9 | T21-05 | OSM, MSS, ZTS | midden | Op 419 zusterpagina's wijst `og:url` naar de homepage, of op ZTS naar een niet-bestaande `helpcenter.html`, in plaats van naar de pagina zelf. |
| 10 | T21-34, T21-35 | AIBM | midden | De agent-route spreekt de pagina's tegen. llms.txt verwijst naar 7 niet-bestaande en 9 niet-canonieke URL's, en bij 32 producten verschilt de API-prijs van de Offer-prijs in de JSON-LD van de review. |

### Wat technisch goed is (gecontroleerd, geen bevinding)

- 0 ongeldige JSON-LD-blokken op 6.293 blokken. Er is geen enkele `AggregateRating` en geen self-serving review-markup (script 03).
- 0 noindex-pagina's en 0 niet-bestaande pagina's in de vier sitemap.xml-bestanden (script 01).
- 0 gebroken interne links op AIBM, OSM en ZTS (script 02). MSS: alleen op de noindex-pagina `/preview/` (T21-13).
- Alle 7.585 links van AIBM naar de zusters en alle 12.701 links van de zusters naar AIBM en elkaar hebben `nofollow` (script 02).
- Alle herkende affiliatelinks (AIBM 2.326, OSM 819, MSS 1.232, ZTS 228) hebben `sponsored` of `nofollow`. De enige treffer zonder rel (MSS, `go.bidx.io/knowledge/...`) is een kennisbanklink en geen affiliatelink (script 02).
- Er zijn geen bijna-identieke pagina's binnen één site: geen enkel paar indexeerbare pagina's haalt Jaccard ≥ 0,50 op eigen tekst. Het hoogste paar is AIBM `pricewatch/log-2026-08` ↔ `log-2026-09` met 0,47 (script 04).
- De hreflang-set van `research/saas-pricing-transparency-2026` (en, de, es, fr, pt, x-default) is wederkerig en zelf-canoniek (script 01).
- Elke indexeerbare pagina heeft een viewport, een `lang`, een unieke title, een unieke description en een unieke H1. De enige uitzondering zijn 3 AIBM-embedfragmenten (T21-09) (script 06).
- Op geen van de 814 gerenderde pagina's verandert JavaScript de title, canonical, robots of H1 (script 09, T21-26).

### Tellingen per gebied en per site

Een bevinding die meerdere sites raakt, telt bij elke site mee.

| Gebied | AIBM | OSM | MSS | ZTS | Totaal codes | hoog | midden | laag |
|---|---|---|---|---|---|---|---|---|
| 1 Indexeerbaarheid (T21-01 – 10) | 8 | 3 | 4 | 4 | 10 | 1 | 5 | 4 |
| 2 Interne links (T21-11 – 14) | 3 | 2 | 3 | 3 | 4 | 0 | 2 | 2 |
| 3 Structured data (T21-15 – 21) | 7 | 4 | 4 | 4 | 7 | 0 | 1 | 6 |
| 4 Spam-update-risico's (T21-22 – 26) | 4 | 5 | 5 | 4 | 5 | 0 | 2 | 3 |
| 5 Kwaliteit en weergave (T21-27 – 31) | 5 | 4 | 4 | 4 | 5 | 0 | 0 | 5 |
| 6 Toegankelijkheid en mobiel (T21-32 – 33) | 2 | 1 | 1 | 1 | 2 | 0 | 0 | 2 |
| 7 Agent-/AI-route (T21-34 – 38) | 5 | 3 | 3 | 3 | 5 | 0 | 2 | 3 |
| **Totaal** | **34** | **22** | **24** | **23** | **38** | **1** | **12** | **25** |

Status: 30 CONFIRMED, 8 PLAUSIBLE (T21-07, T21-14, T21-22, T21-23, T21-24, T21-28, T21-30, T21-38). Bij T21-01 zijn de tellingen CONFIRMED; het gevolg (Google negeert de canonical) is PLAUSIBLE.

### Kerncijfers (script 01, 02)

| | AIBM | OSM | MSS | ZTS |
|---|---|---|---|---|
| HTML-pagina's in repo (excl. 404) | 2.044 | 170 | 231 | 73 |
| noindex (robots) | 1.319 | 10 | 18 | 2 |
| alleen googlebot-noindex (snoeiproef) | 36 | 0 | 0 | 0 |
| canonical naar zuster | 385 | 0 | 0 | 0 |
| indexeerbaar en zelf-canoniek (incl. pagina's zonder canonical) | 304 | 160 | 213 | 71 |
| URL's in sitemap.xml | 306 | 160 | 213 | 71 |
| URL's in sitemap-video.xml | 247 | 72 | 90 | 40 |
| URL's in sitemap-verwijderd.xml | 2.865 | – | – | – |
| linkdiepte zelf-canonieke indexeerbare pagina's (0/1/2/3/onbereikbaar) | 1/44/248/2/6 | 1/37/122/0/0 | 1/44/168/0/0 | 1/31/38/0/1 |

---

## Bevindingen

Opbouw per bevinding: site · ernst · URL/pad · wat er staat · waarom het een probleem is · oplossing · status.

### Gebied 1: Indexeerbaarheid

#### T21-01: 327 indexeerbare AIBM-reviewkopieën zijn ingekorte versies met een canonical naar de zuster
- **Site:** AIBM · **Ernst:** hoog · **Status:** CONFIRMED (tellingen). Of Google de canonical werkelijk negeert is PLAUSIBLE, want Search Console is niet ingezien.
- **URL/pad:** 385 AIBM-pagina's hebben een canonical naar een zuster: `b2b/` 328, `tools/` 25, `best/` 17, `deals/` 10, `build/` 5. De 57 niet-b2b-pagina's zijn echte duplicaten (Jaccard 0,83–0,99 op eigen tekst). Daar is de canonical correct, al blijft een 301 schoner. Het probleem zit in de 328 `b2b/`-kopieën, waarvan er 327 indexeerbaar zijn (`b2b/learnworlds-review/` heeft googlebot-noindex). Voorbeeld: `/b2b/adp-review/`.
- **Wat er staat:** `<link rel="canonical" href="https://officesoftwaremarketplace.com/adp-review.html">`, zonder noindex (`<meta name="robots" content="max-image-preview:large">`). De AIBM-pagina telt 863 woorden zichtbare tekst, de zuster 3.133. Over de 328 b2b-paren is dat mediaan 987 tegen 2.881 woorden. 60–90% van de eigen AIBM-tekst staat ook op de zuster (containment), maar de Jaccard-overlap ligt bij alle 328 onder 0,5 (mediaan ±0,3). De AIBM-pagina is dus een uittreksel van de zusterreview (script 04, deel C).
- **Waarom:** rel=canonical is een hint die Google alleen volgt bij (bijna-)duplicaten. Een pagina met ruwweg een derde van de tekst is een uittreksel en geen duplicaat. Volgt Google de hint niet, dan kiest Google zelf, en AIBM levert daarbij sterkere signalen: 5.549 interne links (T21-11), de `/b2b/`-hub, de eigen breadcrumbs en JSON-LD-URL's (T21-16). In het slechtste geval staan er dan 327 dunne kopieën van zusterreviews in de index, met dezelfde eigenaar, hetzelfde sjabloon en dezelfde video's. Na de spam-update is dat het patroon dat je niet wilt laten zien.
- **Oplossing:** maak van de 328 b2b-URL's een server-side **301** naar de zuster-URL. In de opdracht staat dat dit voor een deel al zo is. In de repo is het niet te zien, dus controleer met `curl -I` welke live al 301 geven. Waar een 301 nu niet kan: zet `noindex, follow` op de AIBM-kopie, houd de canonical aan en haal de kopie uit de `/b2b/`-hub. Voor de 57 echte duplicaten (`tools/`, `best/`, `deals/`, `build/`) volstaat de canonical; een 301 is daar optioneel.

#### T21-02: AIBM-sitemap bevat 5 URL's met een canonical naar een zuster
- **Site:** AIBM · **Ernst:** midden · **Status:** CONFIRMED (script 01: `sitemap_bevat_canonical_elders`)
- **URL/pad:** `sitemap.xml` → `/build/business-finance-stack/`, `/build/cold-outreach-system/`, `/build/content-engine/`, `/build/customer-support-system/`, `/build/shopify-store-stack/`
- **Wat er staat:** in de sitemap `<loc>https://aibuildermarketplace.com/build/business-finance-stack/</loc> <lastmod>2026-08-12</lastmod>`; op de pagina `<link rel="canonical" href="https://officesoftwaremarketplace.com/build-business-finance-stack.html">`.
- **Waarom:** een sitemap hoort alleen canonieke URL's te bevatten. Hier staan twee tegenstrijdige signalen voor dezelfde pagina, terwijl de snoeiproef juist uitgaat van een zuivere sitemap.
- **Oplossing:** haal de 5 URL's uit `sitemap.xml`. Neem in de sitemap-generator een check op: alleen URL's waarvan de canonical gelijk is aan de URL zelf.

#### T21-03: Sitemap-lastmod klopt niet met dateModified en de zichtbare datum (alle vier)
- **Site:** AIBM, OSM, MSS, ZTS · **Ernst:** midden · **Status:** CONFIRMED (script 08)
- **URL/pad:** `sitemap.xml` van alle vier
- **Wat er staat:** `<loc>https://aibuildermarketplace.com/b2b/1password-review/</loc> <lastmod>2026-10-20</lastmod>`, terwijl de pagina zelf `"dateModified": "2026-10-01"` en zichtbaar "Updated 2026-10-01" heeft. Tellingen:

  | site | URL's met dateModified | lastmod ≠ dateModified | lastmod ≠ zichtbare "Updated" | lastmod-verdeling |
  |---|---|---|---|---|
  | AIBM | 251 | 223 (89%) | 188 van 208 | 203× 2026-10-20 |
  | OSM | 133 | 124 (93%) | 117 van 125 | alleen 21, 20 en 14 okt |
  | MSS | 180 | 166 (92%) | 157 van 169 | alleen 21, 20 en 14 okt |
  | ZTS | 59 | 54 (92%) | 49 van 53 | 20, 21, 14 en 15 okt |

  Op AIBM zette de commit van 20 okt ("Alle reviews herbouwd: blok 'In X's own words' …", `2e7c4196`) de lastmod van ±160 URL's in één keer op 2026-10-20. De zusters krijgen elke dag de commit "Daily sister refresh … sitemap".
- **Waarom:** Google gebruikt lastmod alleen zolang die "consistent en aantoonbaar juist" is. Een lastmod die meegaat met sjabloon-rebuilds leert Google het veld te negeren. Dan kost het juist meer tijd voordat echte inhoudelijke verbeteringen (de snoeiproef-upgrades) opnieuw gecrawld worden. Daarnaast is "alles is vandaag gewijzigd" een versheidssignaal dat niet klopt met de pagina.
- **Oplossing:** laat de generator lastmod nemen uit dezelfde bron als `dateModified` (de inhoudelijke wijzigingsdatum) en niet uit de bouwdatum. Een wijziging aan nav, footer of kaarten is geen reden voor een nieuwe lastmod. De `<changefreq>`/`<priority>` in de AIBM-sitemap mogen weg; Google negeert ze.

#### T21-04: Videositemaps wijzen naar de verkeerde pagina's
- **Site:** AIBM (fout opgenomen), OSM, MSS, ZTS (ontbrekend) · **Ernst:** midden · **Status:** CONFIRMED (script 01, 08)
- **URL/pad:** `sitemap-video.xml` van alle vier
- **Wat er staat:**
  - AIBM: van 247 items zijn er 19 googlebot-noindex (bv. `/b2b/airwallex-review/`) en 24 met een canonical naar een zuster. Bij die 24 staat de video niet eens op de pagina. Voorbeeld: `<loc>https://aibuildermarketplace.com/b2b/auware-review/</loc>` met `<video:player_loc>…/embed/0xbiognwnKE`, terwijl `/b2b/auware-review/index.html` 0 `<iframe>`'s heeft.
  - Diezelfde video staat wél ingebed op `marketingandsalessoftware.com/auware-review.html`, maar die pagina ontbreekt in de MSS-videositemap.
  - Indexeerbare pagina's met VideoObject die niet in de eigen videositemap staan: OSM 37, MSS 56, ZTS 4, AIBM 1 (`/b2b/seamless-ai-review/`).
- **Waarom:** Google indexeert een video op de pagina waar hij zichtbaar is ingebed. Een videositemap die naar een pagina zonder video wijst, of naar een noindex- of niet-canonieke pagina, levert fouten op ("video niet gevonden op pagina", "geen canonieke pagina"). Bovendien ontbreken de juiste pagina's.
- **Oplossing:** genereer elke videositemap uit de pagina's die de video echt insluiten en die indexeerbaar en zelf-canoniek zijn. Verplaats de 24 verhuisde items naar de zuster-videositemaps en verwijder de 19 noindex-items zolang de snoeiproef loopt.

#### T21-05: `og:url` wijst op de zusters naar de homepage of naar een niet-bestaande pagina
- **Site:** OSM (151), MSS (205), ZTS (63) · **Ernst:** midden · **Status:** CONFIRMED (script 01: `og_url_wijkt_af`)
- **URL/pad:** bv. `officesoftwaremarketplace.com/adp-review.html`, `zerotouchsupport.com/aircall-review.html`
- **Wat er staat:** OSM: `<meta property="og:url" content="https://officesoftwaremarketplace.com/">`; ZTS: `<meta property="og:url" content="https://zerotouchsupport.com/helpcenter.html">`, terwijl `helpcenter.html` niet in de repo staat. Daarnaast hebben 145 (OSM), 193 (MSS) en 68 (ZTS) pagina's dezelfde `og:image` (`/og.png`). AIBM heeft per review een eigen OG-afbeelding.
- **Waarom:** een gedeelde review verschijnt op sociale netwerken en in chat-previews als de homepage. Voor zoekmachines is het een URL-signaal dat de canonical tegenspreekt. Google canonicaliseert niet primair op og:url, maar het telt mee als ruis, en op ZTS wijst het naar een 404.
- **Oplossing:** zet `og:url` gelijk aan de canonical van de pagina, en geef reviews een eigen OG-afbeelding zoals op AIBM.

#### T21-06: Meta-refresh-stubs met tegenstrijdige signalen en een canonical-keten
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED voor de bestanden; PLAUSIBLE voor het live gedrag (een server-301 zou de stub overrulen)
- **URL/pad:** 13 bestanden: `/800.html`, `/deals.html`, `/finder.html`, `/synthesia-review-2026.html` en 9× `/guides/*-alternatives/` (asana, dropbox, expensify, hootsuite, hubspot, outreach, ringcentral, salesforce, zoominfo)
- **Wat er staat:** `800.html`: `<meta http-equiv="refresh" content="0; url=/b2b/800-com-review/">` + `<link rel="canonical" href="https://aibuildermarketplace.com/b2b/800-com-review/">` + `noindex,follow`, terwijl `/b2b/800-com-review/` zelf een canonical naar `zerotouchsupport.com/800-com-review.html` heeft. Dat is een keten van 2 stappen. De 9 guides verwijzen allemaal met refresh en canonical naar de hub `/guides/` en staan ook in `sitemap-verwijderd.xml`. `/finder.html` verwijst naar `/build/`, dat noindex is. `/synthesia-review-2026.html` heeft refresh en canonical, maar geen noindex.
- **Waarom:** een refresh naar een algemene hub telt bij Google als soft-404. Een canonical naar een pagina die zelf weer doorverwijst is een keten. noindex plus een canonical elders zijn tegenstrijdige signalen.
- **Oplossing:** maak er server-side 301's (direct naar het eindadres, bij 800.html dus naar ZTS) of 410's van, en verwijder de stub-bestanden. Laat de guides 410 geven, of een 301 naar een inhoudelijk gelijkwaardige pagina.

#### T21-07: `sitemap-verwijderd.xml` met 2.865 verwijderde URL's staat in robots.txt
- **Site:** AIBM · **Ernst:** laag · **Status:** PLAUSIBLE (de live status van de URL's is niet gezien)
- **URL/pad:** `/robots.txt` → `Sitemap: https://aibuildermarketplace.com/sitemap-verwijderd.xml` (395× `/alternatives/`, 340× `/deals/`, 333× `/vs/`, 36× `/solve/` …)
- **Wat er staat:** 2.865 `<loc>`'s met `<lastmod>2026-08-11</lastmod>`. Daarvan staan er 9 nog als bestand in de repo: de refresh-guides uit T21-06.
- **Waarom:** tijdelijk verwijderde URL's in een sitemap zetten om ze sneller te laten herkruipen is een bekende tactiek. Blijft de sitemap staan, dan geeft Search Console duizenden fouten ("ingediende URL niet gevonden") en blijft Google URL's opvragen die weg moeten. Of de URL's live 404, 410 of 301 geven, is vanuit de repo niet te zien.
- **Oplossing:** controleer met `curl -I` een steekproef van 50 URL's (de verwachting is 410). Haal de sitemap weg uit robots.txt zodra Search Console laat zien dat ze uit de index zijn, uiterlijk een paar weken na de opname.

#### T21-08: noindex gecombineerd met een canonical elders
- **Site:** AIBM, MSS · **Ernst:** laag · **Status:** CONFIRMED (script 01: `noindex_en_canonical_elders`)
- **URL/pad:** AIBM `/b2b/learnworlds-review/`; MSS `/preview/`, `/preview/reply-io-review.html`
- **Wat er staat:** `<meta name="googlebot" content="noindex, follow">` + `<link rel="canonical" href="https://marketingandsalessoftware.com/learnworlds-review.html">`
- **Waarom:** Google raadt af om noindex en een canonical naar een andere URL te combineren. Het kan ertoe leiden dat het noindex-signaal op de canonical-doelpagina wordt overgedragen.
- **Oplossing:** kies per pagina één signaal: voor learnworlds een 301 of alleen de canonical, en verwijder MSS `/preview/` (zie T21-13).

#### T21-09: Drie indexeerbare e-mailfragmenten zonder title, H1, viewport, lang en canonical
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 06)
- **URL/pad:** `/deals/embed/crm/email.html`, `/deals/embed/hosting/email.html`, `/deals/embed/security/email.html`
- **Wat er staat:** het bestand begint direct met `<table role="presentation" width="100%" … style="max-width:600px"><tr><td …>CRM deals for small sales teams</td>`. Er is geen `<head>`, geen meta robots, en 117–146 woorden. Wel linkt de (noindex) pagina `/deals/embed/` ernaar.
- **Waarom:** het zijn kale HTML-fragmenten die als zelfstandige pagina indexeerbaar zijn: dun, zonder titel en met affiliatelinks. Juist dat soort pagina's wil het snoeiplan uit de index houden.
- **Oplossing:** geef ze `<meta name="robots" content="noindex">` (of een `X-Robots-Tag` per pad in Caddy), of serveer ze als `.txt`/download.

#### T21-10: Oude dunne artikelen op ZTS staan indexeerbaar naast de reviews
- **Site:** ZTS · **Ernst:** midden · **Status:** CONFIRMED (script 01, 04, 06)
- **URL/pad:** `/800.html` (501 woorden), `/pylon.html` (660), `/surveysparrow.html` (531). Alle drie staan in `sitemap.xml` zonder noindex.
- **Wat er staat:** `<h1>Setting up a Zero-Touch IVR and a professional business line in 10 minutes`, met JSON-LD `"author":{"@type":"Person","name":"Daan",…}` terwijl er geen zichtbare byline is. Voor dezelfde producten staan `800-com-review.html` en `pylon-review.html` in de sitemap. `surveysparrow.html` heeft geen enkele interne link (wees, T21-12). Het sjabloonaandeel is 42% (800), 40% (surveysparrow) en 32% (pylon), tegenover een mediaan van 24% bij de ZTS-reviews (script 04).
- **Waarom:** het zijn dunne pagina's uit een eerdere generatie die met de reviews concurreren. Volgens het snoeiplan horen ze noindex en uit de sitemap.
- **Oplossing:** een 301 naar de bijbehorende review (800 → `800-com-review.html`, pylon → `pylon-review.html`). Voor surveysparrow, dat geen review heeft: noindex en uit de sitemap, of 410.

### Gebied 2: Interne links

#### T21-11: Interne linkwaarde gaat grotendeels naar niet-indexeerbare pagina's
- **Site:** AIBM (vooral), OSM, MSS, ZTS · **Ernst:** midden · **Status:** CONFIRMED (script 02)
- **URL/pad:**
  - AIBM: 5.275 interne links naar 1.256 noindex-pagina's. De grootste ontvangers zijn `/marketplace/compare/` (642×, sitewide), `/tools/timezone-meeting-planner/` (119×), `/marketplace/manage/` (93×) en `/tools/text-cleaner/` (81×). Daarnaast gaan 5.549 links naar 381 eigen pagina's met een canonical elders, zoals `/tools/cac-ltv-calculator/` (149×) en `/tools/invoice-generator/` (121×), en naar de `/b2b/`-kopieën uit T21-01.
  - Zusters: `answers.html` (noindex) wordt sitewide gelinkt (OSM 163×, MSS 216×, ZTS 73×).
  - Van de zusters naar AIBM: 916 links naar AIBM-noindex-pagina's (de footerlink `/handbook/`, de tools) en 58 naar AIBM-kopieën waarvan de canonical naar een andere zuster wijst (bv. MSS `atlas.html` → `aibuildermarketplace.com/b2b/blinq-review/` → OSM).
- **Waarom:** van de 66.123 interne links op AIBM wijst een groot deel naar pagina's die niet in de index mogen. De 304 indexeerbare pagina's krijgen daardoor minder interne autoriteit dan mogelijk is, en de AIBM-kopieën krijgen juist meer, wat T21-01 versterkt.
- **Oplossing:** laat in kaarten en hubs de reviewlinks voor verhuisde producten direct naar de zuster-URL wijzen. Haal sitewide links naar `/marketplace/compare/`, `/handbook/` en `answers.html` uit de footer en de vaste blokken, of geef die pagina's een reden om indexeerbaar te zijn. Laat zusterkaarten voor verhuisde producten naar de canonieke zuster wijzen en niet naar de AIBM-kopie.

#### T21-12: Wezen en pagina's die alleen vanaf noindex-pagina's te bereiken zijn
- **Site:** AIBM, ZTS · **Ernst:** laag · **Status:** CONFIRMED (script 02)
- **URL/pad:**
  - Geen enkele interne `<a href>` naar deze pagina's: AIBM `/black-friday/` (4.216 woorden), `/pricewatch/log-2026-08/`, `/research/saas-pricing-transparency-2026-de/`, `-es/`, `-fr/`, `-pt/` (de vertalingen zijn alleen via `<link rel="alternate" hreflang>` bereikbaar); ZTS `/surveysparrow.html`.
  - Alleen gelinkt vanaf noindex-pagina's: AIBM `/build/ai-agent-build-vs-buy/`, `/build/ai-programmatic-seo/` (alleen vanaf `/build/`, dat noindex is) en `/build/support-plan/`.
  - Linkdiepte is verder geen probleem: alle andere indexeerbare pagina's zitten binnen 3 klikken van de homepage, en de links in `<template>` veranderen daar niets aan.
- **Waarom:** een pagina die alleen via de sitemap te vinden is, krijgt weinig crawlprioriteit en geen interne context.
- **Oplossing:** link `/black-friday/` en het logboek van augustus vanaf `/pricewatch/`, zet een zichtbare taalkeuze op het rapport (links naar de vier vertalingen), en geef de `/build/`-plannen een link vanaf een indexeerbare pagina, of maak ze noindex als ze niet in de index horen.

#### T21-13: MSS `/preview/` linkt 97 keer naar niet-bestaande pagina's
- **Site:** MSS · **Ernst:** laag · **Status:** CONFIRMED (script 02: `gebroken_intern`)
- **URL/pad:** `marketingandsalessoftware.com/preview/` (noindex, nofollow)
- **Wat er staat:** `<a href="/algomo-review.html">`, en zo verder voor 97 AIBM-only reviews. Op MSS bestaan ze niet: `algomo-review.html` staat alleen op AIBM als `/b2b/algomo-review/`.
- **Waarom:** de pagina is noindex/nofollow, dus de schade is klein. Het blijft wel een oude previewpagina die crawlbudget kost en 404's oplevert.
- **Oplossing:** verwijder `/preview/` uit de MSS-repo.

#### T21-14: Netwerklinks tussen de vier sites (rel is in orde, het patroon blijft zichtbaar)
- **Site:** alle · **Ernst:** midden · **Status:** PLAUSIBLE (het effect is niet te meten; de tellingen zijn CONFIRMED)
- **URL/pad:** sitewide footer "Part of the network" en kaarten met "Honest review →"
- **Wat er staat:** AIBM → zusters 7.585 links; OSM → AIBM 4.434, MSS → AIBM 5.711, ZTS → AIBM 1.645, en tussen de zusters onderling 74–218 per richting. Per pagina: AIBM mediaan 3 kruislinks, de zusters mediaan 27–28 (max 204). Allemaal `nofollow`, de meeste met `?utm_source=<site>&utm_medium=ecosystem|footer`. De zusters laden ook `https://aibuildermarketplace.com/shortlist.js` (334 pagina's) en de auteursfoto `…/about/daan-96.jpg` (328) rechtstreeks van AIBM.
- **Waarom:** met nofollow wordt er geen PageRank doorgegeven, en dat is goed. Maar alles samen maakt de vier domeinen voor Google tot één herkenbaar netwerk: wederzijdse sitewide links, cross-domain canonicals (T21-01), hetzelfde sjabloon (T21-22), dezelfde tools op vier domeinen en gedeelde scripts. Bij een spam-update gericht op geschaalde inhoud en netwerken is dat een risicofactor, ook al is elke losse link netjes.
- **Oplossing:** beperk netwerklinks tot één vermelding per pagina (bv. alleen in de footer, zonder UTM). Laat kaarten bij voorkeur naar de eigen site wijzen. Host `shortlist.js` en de auteursfoto per site. Een transparante "één eigenaar"-vermelding is prima; tientallen kruislinks per pagina zijn niet nodig.

### Gebied 3: Structured data

#### T21-15: 298 AIBM-kopieën hebben VideoObject- en Clip-markup zonder video op de pagina
- **Site:** AIBM · **Ernst:** midden · **Status:** CONFIRMED (script 03: `video_geen_embed_element`)
- **URL/pad:** 299 pagina's met een canonical naar een zuster; 298 daarvan zijn indexeerbaar, en `/b2b/learnworlds-review/` heeft googlebot-noindex. Voorbeeld: `/b2b/24-7pressrelease-review/`.
- **Wat er staat:** `{"@type": "VideoObject", "name": "24-7PressRelease Review (2026) — honest pricing & who should skip it", … "embedUrl": "https://www.youtube-nocookie.com/embed/jF54IbRVRcU", "hasPart": [{"@type": "Clip", "name": "The short answer", "startOffset": 0, …`. Op de pagina staat geen `<iframe>` en geen ander embed-element met die video-ID.
- **Waarom:** Google eist dat de video op de pagina zichtbaar is. Markup voor een video die er niet is, beschrijft geen zichtbare inhoud en kan als misleidende structured data gelden. Volgt Google de canonical niet (T21-01), dan concurreert deze markup ook met de echte videopagina op de zuster.
- **Oplossing:** laat het VideoObject-blok weg op pagina's zonder embed. De generator kan dat eenvoudig afleiden: geen iframe, dan geen VideoObject.

#### T21-16: JSON-LD-URL's op AIBM-kopieën wijzen naar AIBM, de canonical naar de zuster
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 03: `app_url_ongelijk_canonical`, 328×)
- **URL/pad:** bv. `/b2b/800-com-review/`
- **Wat er staat:** `"@type": "SoftwareApplication", … "url": "https://aibuildermarketplace.com/b2b/800-com-review/", "review": {"@type": "Review", "url": "https://aibuildermarketplace.com/b2b/800-com-review/" …`, en de BreadcrumbList eindigt op dezelfde AIBM-URL, terwijl de canonical `https://zerotouchsupport.com/800-com-review.html` is.
- **Waarom:** het is één signaal meer dat de AIBM-URL de "echte" pagina is, tegen de canonical in.
- **Oplossing:** lost zich op met T21-01 (301 of noindex). Blijven de pagina's bestaan, gebruik dan in `url`/`review.url` de canonieke URL.

#### T21-17: Auteursnaam in JSON-LD verschilt van de zichtbare byline
- **Site:** alle · **Ernst:** laag · **Status:** CONFIRMED (eigen telling over `Article.author.name` en de tekst "By … Haket")
- **Wat er staat:** JSON-LD `"author": {"@type": "Person", "@id": "https://aibuildermarketplace.com/about/#daan", "name": "Daniel Haket"}` (AIBM 624, OSM 131, MSS 178, ZTS 57). De zichtbare byline is "By Daan Haket" (AIBM 570, OSM 121, MSS 162, ZTS 45). ZTS heeft daarnaast 3 artikelen met `"name":"Daan"` zonder zichtbare byline (`800.html`, `pylon.html`, `surveysparrow.html`).
- **Waarom:** het is geen fout zolang `@id` en de aboutpagina ("About Daan (Daniel Haket)") de twee namen koppelen. Eén vaste naam in beide maakt de auteursentiteit wel eenduidiger. Voor E-E-A-T-achtige herkenning is consistentie goedkoop.
- **Oplossing:** kies één vorm (bv. `"name": "Daan Haket"` met `"alternateName": "Daniel Haket"`) en gebruik die overal.

#### T21-18: Review-markup zonder reviewRating en SoftwareApplication zonder offers
- **Site:** alle · **Ernst:** laag · **Status:** CONFIRMED (script 03)
- **Wat er staat:** alle 899 `Review`-blokken missen `reviewRating`, en 525 `SoftwareApplication`-blokken missen `offers` (AIBM 385, waarvan 143 kopieën; OSM 61, MSS 61, ZTS 18). `positiveNotes`/`negativeNotes` zijn wel aanwezig.
- **Waarom:** het is geen overtreding: zonder rating komt er ook geen sterrenweergave en dus geen risico op self-serving-review-problemen. Het betekent wel dat geen enkele review in aanmerking komt voor een review- of software-rich result, op pros/cons na.
- **Oplossing:** bewust zo laten is verdedigbaar. Zet anders `offers` (met `price` en `priceCurrency`) consequent op elke review met een publieke prijs. Voeg geen ratings toe zonder methodiek.

#### T21-19: VideoObject-`uploadDate` verschilt van de `publication_date` in de videositemap
- **Site:** alle · **Ernst:** laag · **Status:** CONFIRMED (script 08: AIBM 238, OSM 72, MSS 90, ZTS 40)
- **Wat er staat:** pagina `"uploadDate": "2026-07-17T00:00:00+00:00"`; videositemap `<video:publication_date>2026-07-17T08:00:00+00:00</video:publication_date>`
- **Oplossing:** gebruik één bron, bij voorkeur de echte YouTube-publicatietijd.

#### T21-20: Kleine schemafouten: breadcrumbs naar AIBM, verouderd HowTo, Article zonder headline
- **Site:** OSM, MSS, ZTS, AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 03)
- **Wat er staat:** de breadcrumbs van `build-*.html` op de zusters (OSM 1, MSS 3, ZTS 1) bevatten `https://aibuildermarketplace.com/build/`, een ander domein dat bovendien noindex is. Er zijn 10 HowTo-blokken (AIBM 5, OSM 1, MSS 3, ZTS 1); HowTo-rich-results bestaan sinds 2023 niet meer. ItemList-items van het type `Article` zonder `headline`/`author` op `guides.html` (OSM 9, MSS 16, ZTS 10) en AIBM `/ai/` (7).
- **Oplossing:** laat breadcrumbs alleen pagina's van het eigen domein bevatten. HowTo mag blijven, maar levert niets op. Geef de lijstitems `headline` of gebruik `ListItem` met `url` en `name`.

#### T21-21: FAQ-vragen in JSON-LD die niet zichtbaar op de pagina staan
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 03: `faq_vraag_niet_zichtbaar`)
- **URL/pad:** `/b2b/hume-ai-review/` (3 van 4 vragen niet zichtbaar), `/guides/subscription-graveyard/` (1 van 3)
- **Waarom:** FAQ-markup moet overeenkomen met zichtbare inhoud.
- **Oplossing:** maak markup en zichtbare FAQ weer gelijk (genereer beide uit dezelfde bron).

### Gebied 4: Spam-update-risico's

#### T21-22: Hetzelfde sjabloon op vier domeinen, plus paginatypes die op meerdere domeinen indexeerbaar zijn
- **Site:** alle · **Ernst:** midden · **Status:** PLAUSIBLE (het patroon is CONFIRMED; of Google het zo weegt, is niet te bewijzen)
- **Wat er staat:**
  - H2-skelet (script 10): van de 536 indexeerbare reviews over vier sites hebben 535 "How to actually use X" en "Frequently asked questions", en 534 "Pricing (0)", "What X does" en "Others in this category". "Watch the video review" komt 497 keer voor, "What buyers report about X" 421 keer. Per site is de grootste groep met een identiek volledig skelet 26 (AIBM), 12 (OSM), 13 (MSS) en 2 (ZTS).
  - Sjabloonzinnen (script 05): zinnen die (met productnaam → X en cijfers → 0) op 10–90% van de reviews van een site staan. AIBM 23, OSM 35, MSS 31, ZTS 40. Bijvoorbeeld "we have not run x ourselves, so this is other buyers' experience rather than ours." (AIBM 178×, OSM 74×, ZTS 33×) en "across the 0 tools in this category that we researched with a public us-dollar price, the median entry price is $0 a month" (AIBM 156×, OSM 67×). Per pagina is het aandeel in zulke zinnen laag: mediaan 6,6–8,6%, en geen enkele review boven 25%.
  - Op ≥ 2 domeinen indexeerbaar (script 05): `tools/renewal-check` en `tools/software-test-drive` op alle vier (Jaccard 0,23–0,32 op de volledige tekst), `mcp.html` op alle drie de zusters (Jaccard 0,38–0,45 onderling, terwijl AIBM's eigen `/mcp/` noindex is), en verder `atlas`, `finder`, `deals`, `price-watch`, `software`, `guides` en `about`.
- **Waarom:** elke pagina afzonderlijk is geen duplicaat; de eigen tekst verschilt genoeg. Maar het geheel (vier domeinen, één sjabloon, één auteur, dezelfde tools en dezelfde paginatypes) is precies wat een classifier voor "geschaalde inhoud / netwerk van sites" kan oppikken. Alle vier de sites zakten in dezelfde week weg, en dat past bij een signaal op netwerkniveau.
- **Oplossing:** houd elk paginatype op één domein indexeerbaar: tools en MCP op AIBM, met noindex of een canonical naar AIBM op de zusters, of een echt verschillende invulling. Varieer de reviewstructuur per site en per product; de vaste H2's hoeven niet op elke pagina. Begin met de sitebrede blokken die niets per product toevoegen.

#### T21-23: Placeholderblok "Being verified" sinds 20 okt op 560 reviews
- **Site:** AIBM (241), OSM (119), MSS (155), ZTS (45) · **Ernst:** midden · **Status:** PLAUSIBLE (de aanwezigheid is CONFIRMED door tekstzoeken in alle pagina's; de impact niet)
- **URL/pad:** bv. `officesoftwaremarketplace.com/adp-review.html`, sectie "In ADP's own words"
- **Wat er staat:** "Verbatim line: Being verified Free trial Being verified not yet matched to a line on the vendor's own pages Refund Being verified not yet matched to a line on the vendor's own pages A quote appears here only after it matched the live page word for word on the date shown. "Being verified" means we have not matched it yet, not that it does not exist." Op AIBM is het blok ingevoerd met commit `2e7c4196` (20 okt, "Alle reviews herbouwd: blok 'In X's own words' …"). De zusters hebben hetzelfde blok; hun geschiedenis is niet gekloond, dus de exacte datum is daar niet gecontroleerd. Het is in MSS (143×) en OSM (106×) de vaakst voorkomende sjabloonzin.
- **Waarom:** in de herstelperiode kreeg vrijwel elke review hetzelfde blok erbij, dat bij de meeste pagina's alleen placeholdertekst bevat. Dat is extra sjablooninhoud zonder informatie, sitebreed en in één keer: het tegendeel van wat het snoeiplan beoogt ("geen nieuwe paginatypes"; dit is een nieuw bloktype op alle pagina's).
- **Oplossing:** toon het blok alleen als er ten minste één geverifieerd citaat is; laat het anders weg. De status "nog niet geverifieerd" kan in de JSON-API blijven staan.

#### T21-24: Verborgen linklijst op `software.html` van OSM en MSS
- **Site:** OSM, MSS · **Ernst:** laag · **Status:** PLAUSIBLE
- **URL/pad:** `/software.html`: OSM 175 links (378 woorden), MSS 211 links (499 woorden) in een verborgen `<nav>`. ZTS heeft alleen de CSS-regel en geen lijst.
- **Wat er staat:** `<nav aria-label="More reviews" hidden="" id="sw-links"><p><a href="https://aibuildermarketplace.com/b2b/databox-review/?utm_source=officesoftwaremarketplace&amp;utm_medium=ecosystem" rel="nofollow noopener">Databox</a> · <a href="datarails-review.html">Datarails</a> · …</nav><noscript><style>#sw-links{display:block}</style></noscript>`. De overige productkaarten staan in `<template id="sw-rest">` en worden pas ingevoegd na een klik op "Show all 223 tools" of een filterwijziging.
- **Waarom:** met JavaScript, zoals Googlebot rendert, is dit een permanent verborgen lijst van 175 (OSM) of 211 (MSS) links. Dat zijn precies de producten waarvan de kaarten in `<template>` staan (175 en 211 kaarten). De bedoeling (een crawlbare fallback) is legitiem en de links zijn dezelfde als in de kaarten. Toch valt verborgen tekst met veel links onder de richtlijnen voor verborgen tekst/links, en kaarten in `<template>` zijn voor Google geen inhoud.
- **Oplossing:** toon de compacte A–Z-lijst gewoon zichtbaar onder de kaarten (bijvoorbeeld ingeklapt in een `<details>`, wat Google wel als inhoud telt), en schrap het `hidden` + `noscript`-trucje.

#### T21-25: Geen onnatuurlijk sjabloonaandeel of near-duplicates binnen sites (controle)
- **Site:** alle · **Ernst:** laag (informatief) · **Status:** CONFIRMED (script 04)
- **Wat er staat:** geen enkel paar indexeerbare pagina's binnen een site heeft Jaccard ≥ 0,50 (5-shingles; shingles die op ≥ 30% van de pagina's van de site staan, zijn als sjabloon weggefilterd). Paren ≥ 0,30: AIBM 2 (pricewatch-logs), OSM 5 en MSS 3 (`deals-*.html`-pagina's onderling, 0,30–0,37), ZTS 0. De enige pagina's met > 80% sjabloon zijn de drie zuster-`finder.html`'s (84–92% sjabloon, 19–38 eigen shingles).
- **Oplossing:** `finder.html` op de zusters is in wezen een JavaScript-app met een lege schil. Maak die noindex, zoals AIBM al doet met `/finder.html`, of geef hem een inhoudelijke tekst. De `deals-*`-pagina's even in de gaten houden.

#### T21-26: Weergave met en zonder JavaScript: geen cloaking, wel een lege Atlas zonder JS, overloop op mobiel en 2 JS-fouten
- **Site:** alle · **Ernst:** laag · **Status:** CONFIRMED (script 09: 814 pagina's, namelijk alle indexeerbare, de 36 googlebot-noindex-reviews en een steekproef van 30 AIBM-kopieën, elk met en zonder JavaScript in Chromium op 412×915)
- **Wat er staat:**
  - **Geen cloaking-achtige verschillen.** Op geen van de 814 pagina's verandert JavaScript de `<title>`, canonical, meta robots/googlebot of H1. Over alle pagina's samen verschilt het aantal woorden met en zonder JS minder dan 0,4% per site (bv. AIBM 828.418 tegen 831.007).
  - **Inhoud alleen met JS:** AIBM `/atlas/` toont zonder JS 349 woorden en met JS 1.992; 82% van de tekst wordt door JavaScript opgebouwd. `/shopify-app-cost/`: 1.631 tegen 2.345 woorden.
  - **Inhoud alleen zonder JS:** OSM/MSS `software.html` (de verborgen lijst uit T21-24 verschijnt alleen zonder JS) en AIBM `/marketplace/` (3.776 woorden zonder JS, 2.974 met JS).
  - **Horizontale overloop op 412 px:** de `mcp.html` van alle drie de zusters (documentbreedte 745 px), AIBM `/pricewatch/` (467), `/b2b/hume-ai-review/` (452) en `/data/` (423).
  - **JS-fouten:** MSS `best-ai-video-tools.html` en `best-ai-writing-tools.html`: `ReferenceError: fb is not defined`. De afbeeldingen roepen `onerror="fb(this)"` aan, en die functie bestaat op deze twee pagina's niet. Offline faalden alle favicons, maar live gebeurt dit ook bij elk favicon dat niet laadt.
- **Waarom:** Google rendert JavaScript, dus de Atlas is voor Google wel gevuld. AI-crawlers die geen JavaScript uitvoeren, zien op de "Honest Software Atlas" echter alleen de inleiding. Overloop op mobiel geeft horizontaal scrollen, en Google beoordeelt mobiele bruikbaarheid op de gerenderde pagina.
- **Oplossing:** render de Atlas-tabel (of een eerste pagina ervan) server-side in de HTML. Geef de brede tabellen/codeblokken op de 6 pagina's `overflow-x:auto` in een eigen container. Definieer `fb()` in het sjabloon van de best-of-pagina's of verwijder de `onerror`.

### Gebied 5: Kwaliteit en weergave

#### T21-27: Zeer zware HTML op indexeerbare hubpagina's
- **Site:** AIBM, OSM, MSS · **Ernst:** laag · **Status:** CONFIRMED (script 06)
- **Wat er staat:** AIBM `/marketplace/` 1.221 kB HTML, `/atlas/` 1.133 kB, `/b2b/` 1.043 kB, `/deals/` 779 kB, `/finder/` 422 kB. OSM `software.html` 595 kB, MSS `software.html` 680 kB. De mediaan per pagina is 36 kB (AIBM) en 67–87 kB (zusters).
- **Waarom:** het maakt de Core Web Vitals op mobiel trager (parsen en renderen van 1 MB DOM). Op `/b2b/` staan 1.044 links in een `<template>`, en die tellen niet als crawlbare links tot JavaScript ze invoegt. Script 02 laat zien dat dezelfde reviews ook via andere links bereikbaar zijn, dus er ontstaan geen wezen.
- **Oplossing:** pagineer of splits de hubs per categorie, en laad lange lijsten pas na interactie, met een server-side gerenderde eerste pagina.

#### T21-28: Externe afhankelijkheden voor logo's en favicons
- **Site:** OSM, MSS, ZTS (Clearbit), alle (Google-favicons) · **Ernst:** laag · **Status:** PLAUSIBLE
- **Wat er staat:** `<img src="https://logo.clearbit.com/databox.com" alt="Databox" …>` op 853 plekken (OSM 392, MSS 411, ZTS 50), en Google-favicons via `www.google.com` op 11.686 plekken (AIBM 7.620).
- **Waarom:** voor zover mij bekend heeft HubSpot de gratis Clearbit Logo API uitgefaseerd. Dat is niet live gecontroleerd. Geeft het domein geen afbeelding meer, dan tonen 853 kaarten een kapot logo. Externe afbeeldingen zonder `width`/`height` (AIBM 4.940, OSM 1.339, MSS 1.688 en ZTS 356 img's zonder afmetingen) veroorzaken bovendien layout shift.
- **Oplossing:** controleer live of `logo.clearbit.com` nog afbeeldingen levert. Host logo's lokaal, zoals AIBM met `/marketplace/media/`, en geef img's vaste afmetingen.

#### T21-29: Te lange titels en descriptions (klein aantal)
- **Site:** AIBM 6, OSM 1, MSS 3, ZTS 3 titels > 65 tekens; AIBM 5 descriptions > 165 tekens · **Ernst:** laag · **Status:** CONFIRMED (script 06)
- **Wat er staat:** bv. ZTS `price-watch.html`: "Price Watch: what customer support software vendors quietly changed | Zero Touch Support" (88 tekens); AIBM `/research/mcp-pricing-disclosure-2026/`: "74 of 425 SaaS vendors ship an MCP server. 42 don't state which plan you need." (78).
- **Oplossing:** houd titels onder ±60 tekens; laat de merknaam weg waar de titel al lang is.

#### T21-30: Publieke interne bestanden in de webroot (als de repo de webroot is)
- **Site:** AIBM, ZTS · **Ernst:** laag · **Status:** PLAUSIBLE (de serverconfiguratie is niet gezien)
- **Wat er staat:** AIBM: 71 `.py`-scripts in de root (bv. `felix_ceo_agent.py`, `fix_chemicloud_dups.py`), `index.html.backup`, `generate_article.py.broken`, het dashboard `/admin/` ("Victor Command Center … Revenue Intelligence Dashboard", noindex,nofollow) en `/victor.html`. In `robots.txt` staat commentaar met bedrijfscijfers ("de 24.304 affiliate-kliks bij EUR 0,00 omzet"). ZTS: 8 ongebruikte afbeeldingen in de root (`IMG_2365.jpeg` 3,9 MB, `Call Management.png` 3,0 MB …, samen ±24 MB, 0 verwijzingen).
- **Waarom:** het zijn geen rankingfactoren. Wel zijn ze publiek opvraagbaar als de server de repo als webroot gebruikt, en ze geven een rommelige indruk bij handmatige beoordeling (quality raters).
- **Oplossing:** serveer alleen een build-map, of blokkeer `*.py`, `*.backup`, `*.broken`, `/admin/` en `/victor.html` in Caddy. Haal het commentaar uit robots.txt en verwijder de ongebruikte ZTS-afbeeldingen.

#### T21-31: Indexeerbare pagina's met weinig eigen inhoud (JS-schillen en een formulierpagina)
- **Site:** OSM, MSS, ZTS, AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 06, 09)
- **URL/pad:** `/finder.html` op de drie zusters: 255–270 woorden zonder JS, waarvan 84–92% sjabloon (zie T21-25). AIBM `/roadmap/`: 133 woorden met en zonder JS ("Get your AI roadmap — a 30/60/90-day plan … Build my roadmap →"), indexeerbaar en in de sitemap.
- **Waarom:** het zijn pagina's die vooral een tool of formulier zijn, met weinig tekst: het type dat het snoeiplan uit de index wil houden.
- **Oplossing:** noindex en uit de sitemap, of een echte inleidende tekst met uitleg en voorbeeld.

### Gebied 6: Toegankelijkheid en mobiel

#### T21-32: Te weinig contrast in de gedempte tekstkleur
- **Site:** alle · **Ernst:** laag · **Status:** CONFIRMED (script 11, axe-core 4.10 op 17 pagina's; zonder Google Fonts gemeten)
- **Wat er staat:** AIBM `--muted` `#737373` op `#0a0a0a` = 4,17:1 (breadcrumb, ondertitel H1, `.method`, citaten op het transparantierapport). Het "Sister sites"-label `#545a63`/`#575757` op `#0d1117`/`#0a0a0a` = 2,72:1. De verzendknop op `/roi-calculator/` (`#fff` op `#3b82f6`) = 3,67:1. Op OSM/ZTS: "— Daan, AIBuilder Marketplace" `#64748b` op `#1a1f2e` = 3,44:1, en de ZTS-terminaltitel `#475569` op `#0b1329` = 2,43:1. Aantal elementen: AIBM-homepage 21, review 21, transparantierapport 35; OSM/MSS-reviews 1; ZTS-review 21, ZTS best-of 27.
- **Oplossing:** verhoog `--muted` naar ten minste `#8a8a8a` op `#0a0a0a` (± 5,5:1), en maak het netwerklabel en de knop donkerder of lichter.

#### T21-33: Formuliervelden zonder label
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 06, 11)
- **Wat er staat:** `/roi-calculator/`: `<input type="range" id="people" min="1" max="50" value="3">`, en ook `rate`, `hours` en `auto`, zonder `<label for>`. Verder zonder label (alleen placeholder): de zoekvelden op `/atlas/`, `/stack-xray/` en `/stack-auditor/`, het bestandsveld op `/dossier/` en `website` op `/list-your-saas/`. Over alle AIBM-pagina's samen zijn dat 855 velden, vooral op noindex-pagina's.
- **Oplossing:** geef elk veld een `<label for>` of `aria-label`.

### Gebied 7: Agent-/AI-route

#### T21-34: AIBM-llms.txt verwijst naar niet-bestaande en niet-canonieke pagina's en claimt 35 talen
- **Site:** AIBM (de zusters alleen voor `answers.html`) · **Ernst:** midden · **Status:** CONFIRMED (script 07)
- **URL/pad:** `/llms.txt` (91 URL's: 62 indexeerbare pagina's, 10 niet-HTML-bestanden, 2 extern, 7 ontbrekend, 9 canonical elders, 1 noindex)
- **Wat er staat:**
  - Ontbrekend (en opgenomen in `sitemap-verwijderd.xml`): `/b2b/bitvavo-trading-bot/` en `/b2b/replit-trading-bot/` onder "Hands-on reviews (tested by us)" ("Bitvavo, used for months … personal, first-hand account by Daan"), en `/b2b/proton-pricing-en/`, `/b2b/bitvavo-pricing-en/`, `/b2b/beehiiv-pricing-en/` en `/b2b/payoneer-alternatives-en/` onder "Quick recommendations". Daarnaast het sjabloonpad `/api/v1/products/{id}.json`.
  - Canonical elders: `/b2b/foxit-review/`, `/b2b/hostinger-review/` en `/b2b/tresorit-review/` (allemaal naar OSM) en de zes `/best/…`-links.
  - Tekst: "plus comparisons in 35 languages" en "his AI agent Victor, which maintains his sites in 35 languages". De vertaalde vergelijkingspagina's (`/alternatives/*-de/` enz.) staan juist in `sitemap-verwijderd.xml`.
  - `/llms-full.txt` (1.134 URL's) en de llms.txt-bestanden van de zusters zijn wel schoon, op de link naar `answers.html` na, die noindex is (OSM, MSS, ZTS).
- **Waarom:** AI-assistenten en agents krijgen dode links en de niet-canonieke URL's, en lezen claims die de site niet meer waarmaakt. Juist de pagina's die als "hands-on, first-hand" worden aangeprezen, bestaan niet meer.
- **Oplossing:** genereer llms.txt uit dezelfde bron als de sitemap: alleen indexeerbare, zelf-canonieke URL's, met de zuster-URL voor verhuisde reviews. Verwijder de taalclaim en vervang de twee "used for months"-links door de bestaande reviews of door `/about/`.

#### T21-35: API-prijs (`from_price_usd_month`) verschilt van de Offer-prijs in de JSON-LD van de review
- **Site:** AIBM (API) tegen alle vier (pagina's) · **Ernst:** midden · **Status:** CONFIRMED (script 07: 32 producten, vergeleken met de canonieke reviewpagina)
- **Wat er staat (selectie):**

  | product | API `from_price_usd_month` | JSON-LD `Offer.price` (USD) | canonieke review |
  |---|---|---|---|
  | salestarget-ai | 169.0 | 30 | MSS `salestarget-ai-review.html` |
  | seller-snap | 100.0 | 250 | MSS |
  | idrive | 0.25 | 9.99 | OSM |
  | timesact-preorder | 5.0 | 23 | MSS |
  | chatwith | 9.0 | 19 | ZTS |
  | nextify-ai | 29.0 | 21 | MSS |
  | selleasy | 15.0 | 9 | MSS |
  | jane | 59.0 | 79 | OSM |
  | mera-work | 4.0 | 3 | OSM |
  | manychat | 17.0 | 14 | MSS |
  | quillbot | 19.95 | 8.33 | MSS |

  Bij de eerste 9 in de tabel noemen API en markup echt een ander plan of bedrag. Bij manychat en quillbot is de factureringsbasis omgedraaid: de API geeft de maandprijs, de JSON-LD de jaarprijs per maand. De overige 21 zijn het omgekeerde: de API geeft de jaarprijs per maand, de JSON-LD de maandprijs (bv. clickup 7 tegen 10, descript 16 tegen 24, similarweb 125 tegen 199). Volledige lijst: `07_agent_route.json` → `api.prijs_api_vs_jsonld_canonical`.
- **Waarom:** de API presenteert zich als "hand-researched records" voor agents, en de MCP-server leest dezelfde data. Een agent die de API citeert, noemt een andere vanafprijs dan Google uit de markup haalt. Bij de 9 echte verschillen is van buitenaf niet te zien welke klopt, en bij de andere 23 verschilt de basis zonder dat de markup dat aangeeft. De inhoudelijke audit beoordeelt welke prijs juist is; hier gaat het om de technische tegenspraak.
- **Oplossing:** laat JSON-LD `Offer.price` en API `from_price_usd_month` uit één veld komen, met dezelfde factureringsbasis. Leg die basis vast in de API (`entry_price_terms` doet dat al) en in de markup (`priceSpecification` met `billingDuration`).

#### T21-36: API-links naar noindex-pagina's
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED (script 07)
- **Wat er staat:** `links.marketplace` wijst bij 639 van de 641 producten naar een noindex-pagina (`/marketplace/<id>/`). `links.review` wijst bij 35 producten naar een googlebot-noindex-review uit de snoeiproef. De review-links van verhuisde producten wijzen wel al correct naar de zuster.
- **Waarom:** voor agents is noindex geen probleem. Wordt de API als "bron" geciteerd, dan wijst hij wel naar pagina's die je zelf niet in Google wilt.
- **Oplossing:** laat `links.marketplace` weg of vervang het door de review-URL. Het is aanvaardbaar om dat tijdens de snoeiproef zo te laten.

#### T21-37: Tegenstrijdige MCP-aantallen
- **Site:** AIBM · **Ernst:** laag · **Status:** CONFIRMED
- **Wat er staat:** titel van `/research/mcp-pricing-disclosure-2026/`: "74 of 425 SaaS vendors ship an MCP server"; `api/v1/index.json`: `"with_vendor_mcp": 78`; `llms.txt`: "79 of the 425 we track".
- **Oplossing:** één bron, of een datum bij elk getal ("74 op 1 okt; 79 op 21 okt").

#### T21-38: MCP- en API-verwijzingen zijn te controleren, het live endpoint niet
- **Site:** alle · **Ernst:** laag · **Status:** PLAUSIBLE
- **Wat er staat:** alle vier noemen `https://api.aibuildermarketplace.com/mcp` en `https://aibuildermarketplace.com/mcp/atlas_mcp.py`. Het `.py`-bestand en `/api/v1/openapi.json` bestaan in de repo; alle niet-variabele OpenAPI-paden hebben een bestand. Alle 647 JSON-bestanden onder `/api/v1/` zijn geldige JSON, en de tellingen in `index.json` (641 producten, 568 researched, 73 not researched) kloppen met de bestanden. Live verkeer naar de domeinen was in deze omgeving geblokkeerd, dus het endpoint zelf is niet getest.
- **Oplossing:** controleer het MCP-endpoint live (bijvoorbeeld een `tools/list`-aanroep). Verder geen actie.

---

## Wat niet kon en wat de volgende stap is

1. **Live statuscodes.** Draai vanaf een machine met internettoegang:
   `while read u; do printf "%s " "$u"; curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" "$u"; done < urls.txt`
   voor (a) de 385 AIBM-URL's met een canonical naar een zuster (T21-01), (b) een steekproef van 50 uit `sitemap-verwijderd.xml` (T21-07), (c) de 13 refresh-stubs (T21-06) en (d) de 7 ontbrekende llms.txt-URL's (T21-34).
2. **Search Console**, rapport "Pagina's": staan de AIBM-kopieën als "Alternatieve pagina met correcte canonieke tag" of als "Dubbele pagina, Google heeft een andere canonieke versie gekozen dan de gebruiker"? Dat beslist of T21-01 van PLAUSIBLE naar CONFIRMED gaat.
3. **Clearbit-logo's** live controleren (T21-28).

## Methode in het kort

- `lib.py` parseert alle 2.522 HTML-bestanden (BeautifulSoup/lxml) en mapt bestand ↔ URL (`x/index.html` → `/x/`, `x.html` → `/x.html`). Links worden opgelost zoals GitHub Pages/Caddy dat doen.
- "Indexeerbaar" = geen `noindex` in `robots` of `googlebot`, geen meta-refresh, en een canonical die gelijk is aan de eigen URL (of geen canonical).
- Gelijkenis: zichtbare tekst (zonder script/style/noscript/template/svg) → woord-5-shingles. Shingles op ≥ 30% van de pagina's van een site gelden als sjabloon en tellen niet mee. Daarna Jaccard en containment.
- Weergave: Chromium (Playwright 1.56) met en zonder JavaScript, viewport 412×915. Alle verzoeken naar de vier domeinen komen uit de lokale bestanden, alle andere externe verzoeken worden geblokkeerd.
- Toegankelijkheid: axe-core 4.10.3, regels color-contrast, label, button-name, link-name, image-alt, html-has-lang, meta-viewport, document-title, select-name, frame-title, heading-order.
