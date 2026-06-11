#!/usr/bin/env python3
"""De Groeipiloot — wekelijkse autonome optimalisatiecyclus.

Leest Search Console + GA4, kiest de hoogste-impact verbeteringen, voert ze
uit en rapporteert via Telegram (of naar bestand als Telegram niet is
geconfigureerd).

Fase 1 (deze versie):
  KIJKEN   - GSC: pagina's met veel vertoningen, lage CTR, positie 6-20
           - GA4: affiliate_click per pagina/partner (informatief in rapport)
  DOEN     - Title + meta description herschrijven voor de beste kandidaten,
             via LLM (OpenRouter), ALLEEN Engelstalige pagina's (lang="en")
             zodat de localize_titles-cron er nooit mee botst.
  LEREN    - Wijzigingen worden gelogd; volgende runs meten voor/na-CTR van
             eerdere wijzigingen en rapporteren het effect.

Veiligheid:
  - Zonder --apply: alleen aanbevelen (niets geschreven, niets gepusht).
  - Max MAX_CHANGES wijzigingen per run; nooit URL's of content-body aanraken.
  - Alleen <title>/og:title/twitter:title + meta/og/twitter description.
  - Alles gecommit via git -> victor-staging -> automerge (terugdraaibaar).

Vereist op de VPS (in /root/felix_hq/.env):
  GOOGLE_APPLICATION_CREDENTIALS=/root/felix_hq/gcp_credentials.json
  OPENROUTER_API_KEY of OPENROUTER_KEY     (voor de herschrijvingen)
  GA4_PROPERTY_ID=123456789                (optioneel; GA4-blok slaat over zonder)
  TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... (optioneel; anders rapport naar bestand)

Gebruik (binnen de venv):
  /root/felix_hq/env/bin/python3 /root/felix_hq/groeipiloot.py            # aanbevelen
  /root/felix_hq/env/bin/python3 /root/felix_hq/groeipiloot.py --apply    # uitvoeren
"""
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/root/felix_hq/repos/aibuildermarketplace")
LOG = Path("/root/felix_hq/groeipiloot_log.json")
REPORT_FILE = Path("/root/felix_hq/groeipiloot_rapport.md")
SITE = "aibuildermarketplace.com"
MAX_CHANGES = 10
MIN_IMPRESSIONS = 30
LOOKBACK_DAYS = 28
PSEO_MODEL = os.environ.get("PSEO_MODEL", "anthropic/claude-sonnet-4.5")


# ---------- hulpfuncties ----------

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout


def load_log():
    if LOG.exists():
        return json.loads(LOG.read_text(encoding="utf-8"))
    return []


def save_log(entries):
    LOG.write_text(json.dumps(entries, indent=1, ensure_ascii=False), encoding="utf-8")


def extract_json(text):
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e <= s:
        raise ValueError("geen JSON in LLM-output")
    return json.loads(text[s:e + 1])


# ---------- KIJKEN: Search Console ----------

def gsc_service():
    from googleapiclient.discovery import build
    return build("searchconsole", "v1")


def gsc_property(svc):
    """Vind het juiste property-formaat (sc-domain: of url-prefix)."""
    sites = [s["siteUrl"] for s in svc.sites().list().execute().get("siteEntry", [])]
    for cand in (f"sc-domain:{SITE}", f"https://{SITE}/", f"https://www.{SITE}/"):
        if cand in sites:
            return cand
    sys.exit(f"❌ {SITE} niet gevonden in GSC-properties: {sites}")


def gsc_query(svc, prop, start, end, dimensions, row_limit=2500, dim_filters=None):
    body = {"startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": dimensions, "rowLimit": row_limit}
    if dim_filters:
        body["dimensionFilterGroups"] = [{"filters": dim_filters}]
    return svc.searchanalytics().query(siteUrl=prop, body=body).execute().get("rows", [])


def find_candidates(svc, prop):
    """Pagina+query-combinaties met vertoningen maar te weinig kliks."""
    end = datetime.date.today() - datetime.timedelta(days=2)
    start = end - datetime.timedelta(days=LOOKBACK_DAYS)
    rows = gsc_query(svc, prop, start, end, ["page", "query"])
    cands = {}
    for r in rows:
        page, query = r["keys"]
        imp, clicks, pos = r["impressions"], r["clicks"], r["position"]
        if imp < MIN_IMPRESSIONS or not (6 <= pos <= 20):
            continue
        ctr = clicks / imp if imp else 0
        if ctr >= 0.03:
            continue
        # kans-score: vertoningen x (verwachte ctr op die positie - huidige)
        expected = max(0.04, 0.25 / pos)
        opp = imp * max(0.0, expected - ctr)
        d = cands.setdefault(page, {"page": page, "queries": [], "opp": 0.0})
        d["queries"].append({"q": query, "imp": imp, "clicks": clicks, "pos": round(pos, 1)})
        d["opp"] += opp
    out = sorted(cands.values(), key=lambda d: -d["opp"])
    for d in out:
        d["queries"].sort(key=lambda q: -q["imp"])
        d["queries"] = d["queries"][:5]
    return out


def page_to_file(page_url):
    path = re.sub(r"^https?://[^/]+", "", page_url).split("?")[0]
    if path.endswith("/"):
        path += "index.html"
    f = REPO / path.lstrip("/")
    return f if f.exists() else None


def page_info(f):
    h = f.read_text(encoding="utf-8")
    lang = re.search(r'<html[^>]*lang="([^"]+)"', h)
    title = re.search(r"<title>(.*?)</title>", h, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h)
    return {"lang": (lang.group(1) if lang else "?").split("-")[0],
            "title": " ".join(title.group(1).split()) if title else "",
            "desc": desc.group(1) if desc else ""}


# ---------- DOEN: LLM-herschrijving + toepassen ----------

def llm_rewrite(page, info, queries):
    import requests
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
    if not key:
        sys.exit("❌ geen OPENROUTER_API_KEY/OPENROUTER_KEY in de omgeving")
    qtxt = "\n".join(f"- \"{q['q']}\" ({q['imp']} vertoningen, positie {q['pos']})" for q in queries)
    prompt = f"""Je optimaliseert de title-tag en meta description van een B2B-softwarereviewpagina.

URL: {page}
Huidige title: {info['title']}
Huidige description: {info['desc']}

Zoektermen waarop deze pagina vertoond wordt maar te weinig kliks krijgt:
{qtxt}

Schrijf een betere title en description die de belangrijkste zoekterm natuurlijk
bevatten en de klik verdienen. Regels:
- title: max 60 tekens, GEEN site-naam-suffix (die wordt automatisch toegevoegd),
  GEEN '|' of '-' als scheidingsteken aan het eind, eerlijk en specifiek, geen clickbait.
- BELANGRIJK: noem alleen prijzen, percentages of andere cijfers als die LETTERLIJK
  in de huidige title of description staan. Niets verzinnen of "ongeveer" gokken.
- description: 140-158 tekens, concreet, eerlijk, eindigt niet midden in een zin.
- Taal: Engels.

Antwoord met uitsluitend JSON: {{"title": "...", "description": "..."}}"""
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                      headers={"Authorization": f"Bearer {key}"},
                      json={"model": PSEO_MODEL,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 400},
                      timeout=120)
    r.raise_for_status()
    out = extract_json(r.json()["choices"][0]["message"]["content"])
    t, d = out.get("title", "").strip(), out.get("description", "").strip()
    if not (10 <= len(t) <= 70) or not (80 <= len(d) <= 170):
        raise ValueError(f"LLM-output buiten grenzen (title {len(t)}, desc {len(d)})")
    t = t.replace("|", "-").strip(" -")
    # cijferclaims moeten uit de bestaande tekst komen
    bron = (info["title"] + " " + info["desc"]).lower()
    for num in re.findall(r"\$?\d+[\d.,]*%?", t + " " + d):
        if num.lower() not in bron and num not in ("2025", "2026"):
            raise ValueError(f"niet-verifieerbaar cijfer in LLM-output: {num}")
    return t, d


def apply_rewrite(f, new_title, new_desc):
    h = f.read_text(encoding="utf-8")
    full = f"{new_title} | AIBuilder Marketplace"
    esc = new_desc.replace("&", "&amp;").replace('"', "&quot;")
    esc_t = full.replace("&", "&amp;").replace('"', "&quot;")
    h = re.sub(r"<title>.*?</title>", f"<title>{full}</title>", h, count=1, flags=re.S)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + esc_t + m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + esc_t + m.group(2), h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + esc + m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + esc + m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + esc + m.group(2), h, count=1)
    f.write_text(h, encoding="utf-8")


# ---------- LEREN: effect van eerdere wijzigingen ----------

def evaluate_previous(svc, prop, log):
    lines = []
    today = datetime.date.today()
    for e in log:
        if e.get("evaluated") or e.get("type") != "title":
            continue
        changed = datetime.date.fromisoformat(e["date"])
        if (today - changed).days < 9:
            continue
        def ctr_window(s, t):
            rows = gsc_query(svc, prop, s, t, ["page"],
                             dim_filters=[{"dimension": "page", "operator": "equals", "expression": e["page"]}])
            if not rows:
                return None
            r = rows[0]
            return (r["clicks"], r["impressions"])
        before = ctr_window(changed - datetime.timedelta(days=8), changed - datetime.timedelta(days=1))
        after = ctr_window(changed + datetime.timedelta(days=1), changed + datetime.timedelta(days=8))
        if before and after and before[1] >= 10 and after[1] >= 10:
            b = before[0] / before[1]
            a = after[0] / after[1]
            verschil = (a - b) * 100
            lines.append(f"- {e['page'].split('/b2b/')[-1].rstrip('/')}: CTR {b*100:.1f}% → {a*100:.1f}% ({verschil:+.1f}pt)")
            e["evaluated"] = True
            e["ctr_before"], e["ctr_after"] = round(b, 4), round(a, 4)
    return lines


# ---------- GA4: klik-inzicht ----------

def ga4_clicks():
    prop = os.environ.get("GA4_PROPERTY_ID")
    if not prop:
        return None
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, FilterExpression, Filter
        client = BetaAnalyticsDataClient()
        req = RunReportRequest(
            property=f"properties/{prop}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="yesterday")],
            dimensions=[Dimension(name="customEvent:partner")],
            metrics=[Metric(name="eventCount")],
            dimension_filter=FilterExpression(filter=Filter(
                field_name="eventName", string_filter=Filter.StringFilter(value="affiliate_click"))),
            limit=10,
        )
        resp = client.run_report(req)
        return [(r.dimension_values[0].value, int(r.metric_values[0].value)) for r in resp.rows]
    except Exception as e:
        return [("(GA4-fout: " + str(e)[:80] + ")", 0)]


# ---------- rapport ----------

def send_telegram(text):
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return False
    for chunk in [text[i:i + 3800] for i in range(0, len(text), 3800)]:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat, "text": chunk}, timeout=30)
    return True


def main():
    apply = "--apply" in sys.argv
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        sys.exit("❌ GOOGLE_APPLICATION_CREDENTIALS niet gezet (source /root/felix_hq/.env)")
    log = load_log()
    svc = gsc_service()
    prop = gsc_property(svc)
    print(f"GSC-property: {prop}")

    rapport = [f"🛸 Groeipiloot — {datetime.date.today().isoformat()} ({'UITGEVOERD' if apply else 'AANBEVELINGEN'})", ""]

    # 1. effect van eerdere wijzigingen
    effect = evaluate_previous(svc, prop, log)
    if effect:
        rapport.append("📈 Effect van eerdere wijzigingen (CTR voor → na):")
        rapport.extend(effect)
        rapport.append("")

    # 2. nieuwe kandidaten
    cands = find_candidates(svc, prop)
    recent = {e["page"] for e in log if e.get("type") == "title"
              and (datetime.date.today() - datetime.date.fromisoformat(e["date"])).days < 60}
    changes = 0
    rapport.append(f"🔍 {len(cands)} pagina's met onbenut potentieel gevonden. Top-acties:")
    for c in cands:
        if changes >= MAX_CHANGES:
            break
        if c["page"] in recent:
            continue
        f = page_to_file(c["page"])
        if f is None:
            continue
        info = page_info(f)
        if info["lang"] != "en":
            continue  # fase 1: alleen Engels (geen conflict met localize_titles-cron)
        try:
            new_title, new_desc = llm_rewrite(c["page"], info, c["queries"])
        except Exception as e:
            rapport.append(f"- ⚠️ {c['page']}: LLM-fout, overgeslagen ({str(e)[:60]})")
            continue
        topq = c["queries"][0]
        rapport.append(f"- {c['page']}")
        rapport.append(f"  zoekterm: \"{topq['q']}\" ({topq['imp']} vertoningen, pos {topq['pos']})")
        rapport.append(f"  title:  {info['title'][:70]}")
        rapport.append(f"      →  {new_title} | AIBuilder Marketplace")
        if apply:
            apply_rewrite(f, new_title, new_desc)
            log.append({"type": "title", "date": datetime.date.today().isoformat(),
                        "page": c["page"], "old_title": info["title"], "new_title": new_title,
                        "query": topq["q"]})
        changes += 1
    if changes == 0:
        rapport.append("- geen geschikte kandidaten deze week (of alles recent al aangepast)")
    rapport.append("")

    # 3. GA4-klikinzicht
    clicks = ga4_clicks()
    if clicks:
        rapport.append("💰 Affiliate-kliks per partner (7 dagen):")
        rapport.extend(f"- {p}: {n}" for p, n in clicks)
    elif clicks is None:
        rapport.append("ℹ️ GA4_PROPERTY_ID niet gezet — klikrapport overgeslagen.")
    rapport.append("")

    # 4. publiceren + log
    if apply and changes:
        run(["git", "-C", str(REPO), "add", "-A"])
        run(["git", "-C", str(REPO), "commit", "-m",
             f"groeipiloot: {changes} title/meta-optimalisaties o.b.v. GSC-data"])
        run(["git", "-C", str(REPO), "push", "origin", "main"])  # -> victor-staging -> automerge
        rapport.append(f"✅ {changes} wijzigingen gepusht (live via automerge binnen ~1 uur).")
        save_log(log)
    elif not apply:
        rapport.append("ℹ️ Aanbevelingsmodus — niets gewijzigd. Draai met --apply om uit te voeren.")
    if effect:
        save_log(log)

    tekst = "\n".join(rapport)
    REPORT_FILE.write_text(tekst, encoding="utf-8")
    print("\n" + tekst)
    if send_telegram(tekst):
        print("\n(rapport ook naar Telegram gestuurd)")


if __name__ == "__main__":
    main()
