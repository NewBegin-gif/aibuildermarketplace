"""
Victor Ultra — Autonomous Full-Stack AI Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Claude Sonnet via OpenRouter (fallback: lokale Ollama)
- Full-stack: schrijft code, bouwt websites, debugt, geeft feedback
- Persistent problem-solving: stopt niet tot het opgelost is (/fix)
- Smart article pipeline: 120+ topics, prioriteit op basis van gaps
- Proactieve monitoring: elke 15 min health check, 2x/dag rapport
- Wekelijks strategierapport met AI-analyse (maandag 08:00 UTC)
- SEO, revenue, en strategie commands
- Lange-termijn geheugen + context awareness
"""
import telebot
import subprocess
import time
import os
import json
import threading
import urllib.request
import re
import base64
import tempfile
from datetime import datetime, timedelta
from openai import OpenAI

# ── CONFIG ──────────────────────────────────────────────────────────────────
TOKEN     = "8643600862:AAGYCXeBrexBX4yt8YIhdRiQEGBOqaOH87Y"
ADMIN_ID  = 8311785797
LOG_FILE  = "/root/felix_hq/victor.log"
MEM_FILE  = "/root/felix_hq/victor_memory.json"
LONG_MEM  = "/root/felix_hq/victor_long_memory.json"
REPO_ROOT = "/root/felix_hq/repos/aibuildermarketplace"
TASKS_FILE = "/root/felix_hq/victor_tasks.json"
GSC_CREDENTIALS = "/root/felix_hq/gsc_credentials.json"
GSC_DATA_FILE = "/root/felix_hq/victor_gsc_data.json"
OG_IMAGE_DIR = "/root/felix_hq/repos/aibuildermarketplace/img"

# ── LLM SETUP ───────────────────────────────────────────────────────────────
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
if not OPENROUTER_KEY:
    # Probeer uit .env file
    env_path = "/root/felix_hq/.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("OPENROUTER_KEY="):
                OPENROUTER_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

if OPENROUTER_KEY:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)
    MODEL = "anthropic/claude-sonnet-4"
else:
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    MODEL = "gemma4"

# ── AFFILIATE DATA ──────────────────────────────────────────────────────────
VAULT = {
    "Bitvavo": "https://account.bitvavo.com/create?a=68DCE39715",
    "Replit": "https://replit.com/signup?referral=dglhaket",
    "InVideo": "https://invideo.sjv.io/E00nbn",
    "Synthesia": "https://www.synthesia.io/?via=daniel-haket",
    "Kinsta": "https://kinsta.com/?kaid=EKSCJEFWBYJO",
    "Murf": "https://get.murf.ai/qbhzdrcv3l7x",
}

# ── VICTOR SYSTEM PROMPT ────────────────────────────────────────────────────
SYSTEM_PROMPT = """Je bent Victor — een senior full-stack developer, DevOps engineer, en strategisch adviseur in één. Je hebt ROOT-toegang tot een productie VPS en beheert AIBuilder Marketplace voor Daniel.

## WIE JE BENT

Je bent niet zomaar een bot. Je bent Daniels technische partner:
- Je schrijft productie-klare code (Python, JavaScript, HTML/CSS, bash scripts)
- Je bouwt en verbetert websites en webapplicaties
- Je debugt problemen tot ze ECHT opgelost zijn — niet na 1 poging stoppen
- Je geeft eerlijke, onderbouwde feedback en strategisch advies
- Je denkt mee over business: traffic, conversies, SEO, affiliate revenue
- Je automatiseert alles wat geautomatiseerd kan worden

## HOE JE DENKT

Voordat je IETS doet:
1. Wat is de ECHTE vraag? (niet letterlijk, maar de bedoeling)
2. Heb ik een commando nodig, of is dit een gesprek?
3. Als technisch: wat is de root cause, niet het symptoom?
4. Plan de oplossing EERST, voer dan uit

## WANNEER GEEN COMMANDO'S

- Begroetingen, bedankjes, casual chat → gewoon praten als collega
- Advies, meningen, uitleg → gewoon antwoorden met kennis
- Code review, feedback → analyseer en geef onderbouwd commentaar

## WANNEER WEL COMMANDO'S

Als je een commando moet draaien:
COMMANDO: <exact bash commando>

Regels:
- Max 2 commando's per antwoord
- Leg EERST uit wat je doet en waarom
- Na output: samenvatting in gewone taal

## WAT JE ALLEMAAL KAN

**Code & Development:**
- Python scripts schrijven, debuggen, optimaliseren
- HTML/CSS/JS websites bouwen of aanpassen
- Bash scripts en automatisering
- API integraties bouwen
- Bugs vinden en fixen door logs te analyseren

**DevOps & Server:**
- Server monitoring en beheer
- Cron jobs, systemd services
- Git workflow (commit, push, rebase, conflicts oplossen)
- Performance optimalisatie
- Security checks

**SEO & Marketing:**
- Artikel content genereren en optimaliseren
- Technische SEO (meta tags, structured data, sitemaps)
- Keyword strategie en content planning
- Affiliate link management
- Traffic analyse en aanbevelingen

**Strategie & Advies:**
- Business feedback en aanbevelingen
- Competitie-analyse
- Revenue optimalisatie ideeën
- Prioriteiten stellen: wat heeft de meeste impact?

**Web Design & UI:**
- Professionele landing pages bouwen (dark mode, glassmorphism, gradients)
- Volledige website redesigns met moderne CSS (CSS variables, grid, flexbox, animations)
- Responsive design (mobile-first, tablet, desktop)
- SEO-geoptimaliseerde HTML (structured data, Open Graph, meta tags)
- Conversion-optimalisatie: CTA plaatsing, trust signals, social proof
- Design systeem: consistent kleuren, typography, spacing
- Performance: geen frameworks nodig, pure HTML/CSS/JS is sneller

Wanneer je een pagina/website bouwt:
1. Gebruik ALTIJD het dark theme (--bg-primary:#0a0e17, --accent:#3b82f6) consistent met de rest van de site
2. Google Fonts (Inter) voor typography
3. CSS variables voor theming
4. Scroll animations met IntersectionObserver
5. Mobile-responsive met media queries
6. Structured data (JSON-LD) voor SEO
7. Affiliate links met rel="nofollow sponsored"
8. Maak de HTML COMPLEET en professioneel — geen placeholder tekst

## PERSISTENCE — DIT IS CRUCIAAL

Als iets niet werkt:
1. Analyseer de error — wat is de ROOT CAUSE?
2. Fix het — niet opgeven na 1 poging
3. Verifieer dat de fix werkt
4. Als het nog steeds faalt: probeer een ANDERE aanpak
5. Pas na 3 serieuze pogingen: meld aan Daniel wat er mis is en wat je geprobeerd hebt

Je stopt NOOIT na "het lukt niet". Je bent een engineer — je lost het op.

## OMGEVING

- VPS: Ubuntu 24.04 (187.124.167.150)
- Workspace: /root/felix_hq/
- Site: https://aibuildermarketplace.com (GitHub Pages)
- Repo: /root/felix_hq/repos/aibuildermarketplace/
- Artikel generator: /root/felix_hq/generate_article.py (cron elke 2 uur)
- Index rebuilder: /root/felix_hq/repos/aibuildermarketplace/gen_index.py
- Python venv: /root/felix_hq/venv/

## AFFILIATES
- Kinsta (hosting): https://kinsta.com/?kaid=EKSCJEFWBYJO
- Synthesia (AI video): https://www.synthesia.io/?via=daniel-haket
- InVideo (video): https://invideo.sjv.io/E00nbn
- Replit (coding): https://replit.com/signup?referral=dglhaket
- Bitvavo (crypto): https://account.bitvavo.com/create?a=68DCE39715
- Murf (AI voice): https://get.murf.ai/qbhzdrcv3l7x

## GIT WORKFLOW
Na file wijzigingen:
COMMANDO: cd /root/felix_hq/repos/aibuildermarketplace && git add -A && git commit -m "Victor: <beschrijving>" && git pull --rebase origin main && git push origin main

## SELF-LEARNING & RESEARCH

Je hebt een zelflerend systeem:
- Je onthoudt ELKE fout en de oplossing → je maakt dezelfde fout NOOIT twee keer
- Je slaat werkende oplossingen op als herbruikbare patronen
- Je scant regelmatig het web voor competitor info en SEO trends
- Je analyseert je eigen prestaties en stelt verbeteringen voor
- Je kunt meerdere bestanden tegelijk aanpassen voor complexe refactors

Gebruik /brain om je geleerde kennis te zien, /research voor web scans, /diagnose voor self-analyse.

## MULTI-FILE CODING

Als je complexe taken krijgt die meerdere bestanden raken:
1. Plan EERST welke bestanden je moet aanpassen
2. Lees elk bestand met cat
3. Maak ALLE wijzigingen
4. Test het resultaat
5. Commit alles in één keer

Je kunt Python scripts schrijven die meerdere bestanden tegelijk bewerken — gebruik dit voor bulk operations.

## COMMUNICATIESTIJL

- Nederlands tenzij Daniel Engels praat
- Direct, to-the-point, geen filler
- Casual chat = antwoord als collega, niet als robot
- Gebruik echte cijfers, nooit "veel" of "diverse"
- Als je iets niet weet: zeg dat eerlijk
- Geef constructieve feedback, geen sugarcoating
- Als je code schrijft: leg uit WAAROM je bepaalde keuzes maakt

## OVER DANIEL
Founder, woont in Vietnam. Bouwt AIBuilder Marketplace voor passief affiliate inkomen.
Wil een autonome agent die gewoon dingen regelt zonder micromanagement."""

# ── MEMORY SYSTEM ───────────────────────────────────────────────────────────
def load_memory():
    if os.path.exists(MEM_FILE):
        try:
            return json.load(open(MEM_FILE))
        except:
            pass
    return []

def save_memory(messages):
    with open(MEM_FILE, "w") as f:
        json.dump(messages[-30:], f)

SKILLS_FILE = "/root/felix_hq/victor_skills.json"
RESEARCH_FILE = "/root/felix_hq/victor_research.json"

def load_long_memory():
    if os.path.exists(LONG_MEM):
        try:
            return json.load(open(LONG_MEM))
        except:
            pass
    return {"facts": [], "decisions": [], "errors": [], "wins": [], "patterns": []}

def save_long_memory(mem):
    mem["facts"] = mem["facts"][-50:]
    mem["decisions"] = mem["decisions"][-30:]
    mem["errors"] = mem["errors"][-30:]
    mem["wins"] = mem.get("wins", [])[-30:]
    mem["patterns"] = mem.get("patterns", [])[-20:]
    with open(LONG_MEM, "w") as f:
        json.dump(mem, f, indent=2)

def load_skills():
    """Laad Victor's geleerde vaardigheden en oplossingen."""
    if os.path.exists(SKILLS_FILE):
        try:
            return json.load(open(SKILLS_FILE))
        except:
            pass
    return {"solutions": {}, "code_patterns": [], "avoided": []}

def save_skills(skills):
    skills["code_patterns"] = skills.get("code_patterns", [])[-50:]
    skills["avoided"] = skills.get("avoided", [])[-30:]
    with open(SKILLS_FILE, "w") as f:
        json.dump(skills, f, indent=2)

def load_research():
    """Laad web research resultaten."""
    if os.path.exists(RESEARCH_FILE):
        try:
            return json.load(open(RESEARCH_FILE))
        except:
            pass
    return {"competitors": [], "seo_insights": [], "trends": [], "last_scan": None}

def save_research(data):
    data["competitors"] = data.get("competitors", [])[-20:]
    data["seo_insights"] = data.get("seo_insights", [])[-20:]
    data["trends"] = data.get("trends", [])[-15:]
    with open(RESEARCH_FILE, "w") as f:
        json.dump(data, f, indent=2)

def extract_learnings(user_text, victor_reply):
    """SELF-LEARNING: analyseer elke interactie en sla patronen op."""
    long_mem = load_long_memory()
    skills = load_skills()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Expliciete instructies onthouden
    keywords = ["onthoud", "remember", "belangrijk", "important", "besluit", "decision",
                "voortaan", "from now on", "altijd", "always", "nooit", "never"]
    if any(kw in user_text.lower() for kw in keywords):
        long_mem["facts"].append({"time": ts, "fact": user_text})

    # FOUTEN LEREN: sla error + context op zodat Victor het niet herhaalt
    if "error" in victor_reply.lower() or "failed" in victor_reply.lower() or "❌" in victor_reply:
        error_entry = {"time": ts, "error": victor_reply[:300], "context": user_text[:200]}
        long_mem["errors"].append(error_entry)

        # Zoek een patroon: als dezelfde fout vaker voorkomt, sla op als "avoided"
        error_sig = victor_reply[:80].lower()
        error_count = sum(1 for e in long_mem["errors"] if error_sig[:40] in e.get("error", "").lower())
        if error_count >= 2:
            skills["avoided"].append({
                "time": ts,
                "pattern": error_sig,
                "lesson": f"Deze fout kwam {error_count}x voor. Vermijd deze aanpak."
            })
            save_skills(skills)

    # SUCCESSEN LEREN: als een fix werkt, sla de oplossing op
    success_words = ["opgelost", "gelukt", "succes", "fixed", "✅", "werkt", "done", "klaar"]
    if any(w in victor_reply.lower() for w in success_words):
        long_mem.setdefault("wins", []).append({"time": ts, "win": victor_reply[:200], "task": user_text[:200]})

        # Sla als herbruikbare oplossing op als er een COMMANDO in zat
        if "COMMANDO:" in victor_reply:
            cmds = [p.split("\n")[0].strip().strip('`') for p in victor_reply.split("COMMANDO:")[1:]]
            if cmds:
                # Gebruik de eerste paar woorden van de taak als key
                task_key = re.sub(r'[^a-z0-9 ]', '', user_text.lower())[:60].strip()
                skills["solutions"][task_key] = {
                    "time": ts, "commands": cmds[:3], "description": victor_reply[:150]
                }
                save_skills(skills)

    # CODE PATRONEN LEREN: als Victor code schrijft, sla het patroon op
    code_indicators = ["def ", "function ", "class ", "import ", "#!/"]
    if any(ind in victor_reply for ind in code_indicators):
        # Extract de eerste functie/class definitie
        for line in victor_reply.split("\n"):
            if any(line.strip().startswith(ind) for ind in ["def ", "function ", "class "]):
                skills.setdefault("code_patterns", []).append({
                    "time": ts, "pattern": line.strip()[:100], "context": user_text[:100]
                })
                save_skills(skills)
                break

    save_long_memory(long_mem)

def get_long_memory_context():
    """Geeft ALLE context voor Victor: geheugen + skills + research."""
    long_mem = load_long_memory()
    skills = load_skills()
    research = load_research()
    parts = []

    if long_mem["facts"]:
        parts.append("OPERATOR FACTS:\n" + "\n".join(f"- {f['fact']}" for f in long_mem["facts"][-10:]))

    if long_mem.get("wins"):
        parts.append("RECENT SUCCESSEN (herhaal wat werkt):\n" + "\n".join(
            f"- [{w['time']}] {w['win'][:100]}" for w in long_mem["wins"][-5:]))

    if long_mem["errors"]:
        parts.append("RECENTE FOUTEN (vermijd deze):\n" + "\n".join(
            f"- [{e['time']}] {e['error'][:100]}" for e in long_mem["errors"][-5:]))

    if skills.get("avoided"):
        parts.append("GELEERDE LESSEN (DOE DIT NIET):\n" + "\n".join(
            f"- {a['lesson']}" for a in skills["avoided"][-5:]))

    if skills.get("solutions"):
        recent = sorted(skills["solutions"].items(), key=lambda x: x[1].get("time", ""), reverse=True)[:5]
        if recent:
            parts.append("BEKENDE OPLOSSINGEN:\n" + "\n".join(
                f"- '{k}': {v['description'][:80]}" for k, v in recent))

    if research.get("seo_insights"):
        parts.append("SEO RESEARCH:\n" + "\n".join(
            f"- {i['insight'][:100]}" for i in research["seo_insights"][-3:]))

    if research.get("competitors"):
        parts.append("COMPETITOR INTEL:\n" + "\n".join(
            f"- {c['finding'][:100]}" for c in research["competitors"][-3:]))

    return "\n\n".join(parts) if parts else ""


# ── WEB RESEARCH MODULE ────────────────────────────────────────────────────
def web_research_scan():
    """Scan het web voor competitor data, SEO trends, en affiliate insights."""
    research = load_research()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    findings = []

    # 1. Check eigen site ranking signalen
    try:
        req = urllib.request.Request(
            "https://aibuildermarketplace.com/b2b/",
            headers={"User-Agent": "Victor-Research/1.0"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')
        article_count = html.count('class="card"')
        findings.append(f"Site heeft {article_count} artikel-cards op b2b index")
    except Exception as e:
        findings.append(f"Site check failed: {str(e)[:80]}")

    # 2. Check competitor sites voor ideeen
    competitor_urls = {
        "G2 AI tools": "https://www.g2.com/categories/ai-tools",
        "Capterra AI": "https://www.capterra.com/artificial-intelligence-software/",
    }
    for name, url in competitor_urls.items():
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; research bot)"
            })
            resp = urllib.request.urlopen(req, timeout=15)
            content_length = len(resp.read())
            research["competitors"].append({
                "time": ts, "source": name,
                "finding": f"{name} pagina is {content_length//1024}KB — actieve markt"
            })
        except:
            pass

    # 3. Check affiliate programma pagina's voor updates
    for brand, url in VAULT.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Victor-Research/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            code = resp.getcode()
            page_size = len(resp.read())
            if page_size > 0:
                research["seo_insights"].append({
                    "time": ts,
                    "insight": f"{brand} landing page: {code}, {page_size//1024}KB — link werkt"
                })
        except Exception as e:
            research["seo_insights"].append({
                "time": ts,
                "insight": f"⚠️ {brand} affiliate link probleem: {str(e)[:60]}"
            })

    research["last_scan"] = ts
    save_research(research)
    return findings


def auto_improve_articles():
    """Victor verbetert proactief de slechtste artikelen zonder dat Daniel het vraagt."""
    b2b_path = f"{REPO_ROOT}/b2b"
    worst = find_worst_articles(3)
    improved = []

    for folder, size in worst:
        if size > 5000:  # Alleen echt slechte artikelen (<5KB)
            continue

        article_path = os.path.join(b2b_path, folder, "index.html")
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                old_html = f.read()
        except:
            continue

        brand = folder.split('-')[0].capitalize()
        if brand == 'Invideo':
            brand = 'InVideo'
        if brand.lower() not in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
            continue

        try:
            prompt = f"""Herschrijf dit artikel over {brand} VOLLEDIG. Het is nu maar {size} bytes.

Slug: {folder}
Schrijf minimaal 1500 woorden. HTML tags (geen html/head/body wrapper).
Structuur: H1 headline, intro, features met cijfers, pricing, use case, pros/cons, FAQ (4 vragen), conclusie.
Schrijf als een ervaren founder. Specifieke cijfers, geen vage claims."""

            res = client.chat.completions.create(
                model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=4000
            )
            new_content = res.choices[0].message.content.replace("```html", "").replace("```", "").strip()

            # Gebruik fix_articles.py logica om de HTML proper te wrappen
            fix_script = "/root/felix_hq/fix_articles.py"
            if os.path.exists(fix_script):
                # Schrijf de nieuwe content, dan restyle met fix_articles
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(old_html.split('</head>')[0] + '</head><body>' + new_content + '</body></html>' if '</head>' in old_html else new_content)
                run_command(f"python3 {fix_script}", timeout=120)
            else:
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            new_size = os.path.getsize(article_path)
            improved.append(f"{folder}: {size//1024}KB → {new_size//1024}KB")
            log(f"Auto-improved: {folder}")
        except Exception as e:
            log(f"Auto-improve error {folder}: {e}")

    if improved:
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: auto-improved {len(improved)} articles' && git push origin main")

    return improved


def self_diagnose():
    """Victor analyseert zijn eigen prestaties en stelt verbeteringen voor."""
    long_mem = load_long_memory()
    skills = load_skills()

    error_count = len(long_mem.get("errors", []))
    win_count = len(long_mem.get("wins", []))
    solution_count = len(skills.get("solutions", {}))
    avoided_count = len(skills.get("avoided", []))

    # Analyseer error patronen
    recent_errors = long_mem.get("errors", [])[-10:]
    error_types = {}
    for e in recent_errors:
        err_text = e.get("error", "")[:50].lower()
        for key in ["git", "push", "permission", "timeout", "api", "html", "syntax"]:
            if key in err_text:
                error_types[key] = error_types.get(key, 0) + 1

    report = f"""🧠 Victor Self-Diagnose
━━━━━━━━━━━━━━━━━━━━━━
📊 Statistieken:
  Successen: {win_count}
  Fouten: {error_count}
  Geleerde oplossingen: {solution_count}
  Vermijdpatronen: {avoided_count}
  Success rate: {win_count*100//(win_count+error_count) if (win_count+error_count) > 0 else 0}%

🔍 Meest voorkomende fout-types:"""

    for etype, count in sorted(error_types.items(), key=lambda x: -x[1]):
        report += f"\n  - {etype}: {count}x"

    if not error_types:
        report += "\n  Geen patronen gevonden"

    return report

# ── MODULE 1: GOOGLE SEARCH CONSOLE ────────────────────────────────────────
def setup_gsc():
    """Instructies voor GSC setup. Eenmalig nodig."""
    return """🔧 Google Search Console Setup:

1. Ga naar https://console.cloud.google.com/
2. Maak een project aan (of gebruik bestaand)
3. Enable de "Google Search Console API"
4. Maak een Service Account aan (IAM → Service Accounts)
5. Download de JSON credentials
6. Upload naar VPS: scp credentials.json root@187.124.167.150:/root/felix_hq/gsc_credentials.json
7. Ga naar Google Search Console → Settings → Users → voeg het service account email toe als "Full" user

Stuur me het credentials bestand via Telegram of zet het op de VPS, dan activeer ik het automatisch."""


def fetch_gsc_data(days=28):
    """Haal zoekprestatie data op uit Google Search Console."""
    if not os.path.exists(GSC_CREDENTIALS):
        return None, "GSC credentials niet gevonden. Gebruik /gsc setup"

    try:
        # Dynamisch importeren zodat het niet crasht als google libs niet installed zijn
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            GSC_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        service = build('searchconsole', 'v1', credentials=credentials)

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Top pagina's
        response = service.searchanalytics().query(
            siteUrl='https://aibuildermarketplace.com/',
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page'],
                'rowLimit': 50,
                'dimensionFilterGroups': []
            }
        ).execute()

        pages = []
        for row in response.get('rows', []):
            pages.append({
                'page': row['keys'][0],
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': round(row.get('ctr', 0) * 100, 1),
                'position': round(row.get('position', 0), 1)
            })

        # Top queries
        q_response = service.searchanalytics().query(
            siteUrl='https://aibuildermarketplace.com/',
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': 30
            }
        ).execute()

        queries = []
        for row in q_response.get('rows', []):
            queries.append({
                'query': row['keys'][0],
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': round(row.get('ctr', 0) * 100, 1),
                'position': round(row.get('position', 0), 1)
            })

        data = {
            'pages': sorted(pages, key=lambda x: -x['clicks']),
            'queries': sorted(queries, key=lambda x: -x['impressions']),
            'period': f"{start_date} — {end_date}",
            'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        # Cache opslaan
        with open(GSC_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return data, None

    except ImportError:
        return None, "Google API libraries niet geïnstalleerd. Run: pip install google-auth google-api-python-client"
    except Exception as e:
        return None, f"GSC error: {str(e)[:200]}"


def get_gsc_insights():
    """Analyseer GSC data voor actionable insights."""
    # Probeer eerst cached data
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                data = json.load(f)
        except:
            data = None
    else:
        data = None

    if not data:
        data, err = fetch_gsc_data()
        if err:
            return err

    insights = []

    # Pagina's met hoge impressies maar lage CTR → titel/description verbeteren
    for p in data.get('pages', []):
        if p['impressions'] > 50 and p['ctr'] < 2.0:
            slug = p['page'].split('/b2b/')[-1].rstrip('/') if '/b2b/' in p['page'] else p['page']
            insights.append(f"📈 {slug}: {p['impressions']} impressies maar {p['ctr']}% CTR → verbeter titel/meta")

    # Pagina's met goede positie maar weinig clicks → bijna ranking
    for p in data.get('pages', []):
        if 5 < p['position'] < 15 and p['clicks'] < 5:
            slug = p['page'].split('/b2b/')[-1].rstrip('/') if '/b2b/' in p['page'] else p['page']
            insights.append(f"🎯 {slug}: positie {p['position']} — klein zetje nodig voor pagina 1")

    # Top queries waar we content voor moeten maken
    existing_slugs = set()
    b2b_path = f"{REPO_ROOT}/b2b"
    if os.path.isdir(b2b_path):
        existing_slugs = {f.lower() for f in os.listdir(b2b_path)}

    for q in data.get('queries', []):
        query_slug = q['query'].lower().replace(' ', '-')
        has_content = any(query_slug[:10] in s for s in existing_slugs)
        if not has_content and q['impressions'] > 20:
            insights.append(f"🆕 Query '{q['query']}' ({q['impressions']} impressies) — geen matching artikel!")

    return insights[:15]


# ── MODULE 2: AUTO SITEMAP REBUILD ─────────────────────────────────────────
def rebuild_sitemap():
    """Genereer een verse sitemap.xml op basis van alle bestaande artikelen."""
    b2b_path = f"{REPO_ROOT}/b2b"
    sitemap_path = f"{REPO_ROOT}/sitemap.xml"
    today = datetime.now().strftime('%Y-%m-%d')

    urls = []

    # Homepage
    urls.append(('https://aibuildermarketplace.com/', today, '1.0', 'weekly'))

    # B2B index
    urls.append(('https://aibuildermarketplace.com/b2b/', today, '0.9', 'daily'))

    # Alle artikelen
    if os.path.isdir(b2b_path):
        for folder in sorted(os.listdir(b2b_path)):
            article_path = os.path.join(b2b_path, folder, "index.html")
            if os.path.isfile(article_path):
                # Gebruik file modification time als lastmod
                mtime = os.path.getmtime(article_path)
                lastmod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                urls.append((
                    f'https://aibuildermarketplace.com/b2b/{folder}/',
                    lastmod, '0.7', 'monthly'
                ))

    # Genereer XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, lastmod, priority, changefreq in urls:
        xml += f'  <url>\n'
        xml += f'    <loc>{loc}</loc>\n'
        xml += f'    <lastmod>{lastmod}</lastmod>\n'
        xml += f'    <priority>{priority}</priority>\n'
        xml += f'    <changefreq>{changefreq}</changefreq>\n'
        xml += f'  </url>\n'
    xml += '</urlset>\n'

    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(xml)

    return len(urls)


def rebuild_robots_txt():
    """Zorg dat robots.txt correct verwijst naar de sitemap."""
    robots_path = f"{REPO_ROOT}/robots.txt"
    content = """User-agent: *
Allow: /

Sitemap: https://aibuildermarketplace.com/sitemap.xml
"""
    with open(robots_path, 'w') as f:
        f.write(content)


# ── MODULE 3: OG IMAGE GENERATOR ──────────────────────────────────────────
def generate_og_image(title, brand, output_path):
    """Genereer een professionele OG image (1200x630) met Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False, "Pillow niet geïnstalleerd. Run: pip install Pillow"

    brand_colors = {
        'kinsta': (139, 92, 246),    # purple
        'synthesia': (59, 130, 246), # blue
        'invideo': (167, 139, 250),  # light purple
        'replit': (245, 158, 11),    # amber
        'bitvavo': (16, 185, 129),   # green
        'murf': (236, 72, 153),      # pink
    }

    accent = brand_colors.get(brand.lower(), (59, 130, 246))
    width, height = 1200, 630

    # Achtergrond
    img = Image.new('RGB', (width, height), (10, 14, 23))
    draw = ImageDraw.Draw(img)

    # Gradient top accent bar
    for y in range(6):
        draw.rectangle([(0, y), (width, y)], fill=accent)

    # Bottom gradient glow
    for y in range(80):
        alpha = int(255 * (1 - y / 80) * 0.15)
        color = tuple(min(255, c + alpha) for c in (10, 14, 23))
        draw.rectangle([(0, height - 80 + y), (width, height - 80 + y)], fill=color)

    # Tekst — probeer system fonts
    title_size = 52 if len(title) < 50 else 40 if len(title) < 70 else 32
    try:
        # Probeer beschikbare fonts
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, title_size)
                brand_font = ImageFont.truetype(font_path, 28)
                site_font = ImageFont.truetype(font_path, 20)
                break
        else:
            title_font = ImageFont.load_default()
            brand_font = title_font
            site_font = title_font
    except:
        title_font = ImageFont.load_default()
        brand_font = title_font
        site_font = title_font

    # Brand badge
    badge_text = brand.upper()
    draw.rounded_rectangle([(50, 50), (50 + len(badge_text) * 18 + 30, 95)],
                           radius=8, fill=accent)
    draw.text((65, 55), badge_text, fill=(255, 255, 255), font=brand_font)

    # Title — word wrap
    words = title.split()
    lines = []
    current_line = ""
    max_width = width - 120

    for word in words:
        test_line = f"{current_line} {word}".strip()
        try:
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            w = bbox[2] - bbox[0]
        except:
            w = len(test_line) * title_size * 0.6
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y_start = 140
    for i, line in enumerate(lines[:4]):
        draw.text((60, y_start + i * (title_size + 12)), line,
                  fill=(230, 237, 243), font=title_font)

    # Site naam onderaan
    draw.text((60, height - 60), "aibuildermarketplace.com",
              fill=(100, 120, 140), font=site_font)

    # Opslaan
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG', quality=85)
    return True, output_path


def generate_all_og_images():
    """Genereer OG images voor alle artikelen die er geen hebben."""
    b2b_path = f"{REPO_ROOT}/b2b"
    generated = 0
    errors = 0

    for folder in os.listdir(b2b_path):
        article_path = os.path.join(b2b_path, folder, "index.html")
        if not os.path.isfile(article_path):
            continue

        og_path = os.path.join(OG_IMAGE_DIR, f"{folder}.png")
        if os.path.exists(og_path):
            continue  # Al gemaakt

        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', html)
            title = title_match.group(1) if title_match else folder.replace('-', ' ').title()
            title = title.split('|')[0].split('—')[0].strip()

            # Detect brand
            brand = folder.split('-')[0].capitalize()
            if brand.lower() == 'invideo':
                brand = 'InVideo'

            ok, result = generate_og_image(title, brand, og_path)
            if ok:
                generated += 1

                # Voeg og:image meta tag toe aan artikel als die er niet is
                if 'og:image' not in html:
                    og_url = f"https://aibuildermarketplace.com/img/{folder}.png"
                    og_tags = f'<meta property="og:image" content="{og_url}">\n'
                    og_tags += f'<meta property="og:image:width" content="1200">\n'
                    og_tags += f'<meta property="og:image:height" content="630">\n'
                    og_tags += f'<meta name="twitter:card" content="summary_large_image">\n'
                    og_tags += f'<meta name="twitter:image" content="{og_url}">\n'

                    if '</head>' in html:
                        html = html.replace('</head>', f'{og_tags}</head>')
                        with open(article_path, 'w', encoding='utf-8') as f:
                            f.write(html)
        except Exception as e:
            errors += 1
            log(f"OG image error {folder}: {e}")

    return generated, errors


# ── MODULE 4: TASK PERSISTENCE — CRASH RECOVERY ───────────────────────────
def save_task(task_id, task_type, description, state="running", data=None):
    """Sla lopende taak op zodat Victor na crash verder kan."""
    tasks = load_tasks()
    tasks[task_id] = {
        "type": task_type,
        "description": description,
        "state": state,
        "data": data or {},
        "started_at": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)


def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            return json.load(open(TASKS_FILE))
        except:
            pass
    return {}


def complete_task(task_id):
    """Markeer taak als voltooid."""
    tasks = load_tasks()
    if task_id in tasks:
        tasks[task_id]["state"] = "completed"
        tasks[task_id]["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M')
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)


def fail_task(task_id, reason=""):
    """Markeer taak als gefaald."""
    tasks = load_tasks()
    if task_id in tasks:
        tasks[task_id]["state"] = "failed"
        tasks[task_id]["error"] = reason
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)


def check_interrupted_tasks():
    """Check of er taken zijn die niet zijn afgemaakt (na crash/restart)."""
    tasks = load_tasks()
    interrupted = []
    for tid, task in tasks.items():
        if task.get("state") == "running":
            interrupted.append((tid, task))
    return interrupted


def resume_interrupted_tasks():
    """Probeer afgebroken taken te hervatten na restart."""
    interrupted = check_interrupted_tasks()
    resumed = []

    for tid, task in interrupted:
        task_type = task.get("type", "")
        desc = task.get("description", "")

        if task_type == "restyle":
            # Restyle kan gewoon opnieuw
            try:
                fix_script = "/root/felix_hq/fix_articles.py"
                if os.path.exists(fix_script):
                    run_command(f"cd {REPO_ROOT} && python3 {fix_script}", timeout=120)
                    run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: resumed restyle after restart' && git push origin main")
                    complete_task(tid)
                    resumed.append(f"Restyle hervat en voltooid")
            except:
                fail_task(tid, "Restyle hervatting mislukt")

        elif task_type == "og_images":
            try:
                gen, err = generate_all_og_images()
                if gen > 0:
                    run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: resumed OG image generation ({gen} images)' && git push origin main")
                complete_task(tid)
                resumed.append(f"OG images hervat: {gen} gegenereerd")
            except:
                fail_task(tid, "OG image hervatting mislukt")

        elif task_type == "sitemap":
            try:
                count = rebuild_sitemap()
                rebuild_robots_txt()
                run_command(f"cd {REPO_ROOT} && git add sitemap.xml robots.txt && git commit -m 'Victor: rebuilt sitemap ({count} URLs)' && git push origin main")
                complete_task(tid)
                resumed.append(f"Sitemap rebuild hervat: {count} URLs")
            except:
                fail_task(tid, "Sitemap hervatting mislukt")
        else:
            # Onbekend type → markeer als gefaald
            fail_task(tid, f"Kan taak type '{task_type}' niet hervatten")
            resumed.append(f"Taak '{desc}' kon niet hervat worden")

    return resumed


# ── MODULE 5: KEYWORD-DRIVEN ARTIKEL STRATEGIE ────────────────────────────
def analyze_content_gaps():
    """Analyseer welke keywords/topics missen op basis van GSC data + competitor analyse."""
    gaps = []

    # 1. Check GSC data voor queries zonder matching content
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc = json.load(f)

            existing_slugs = set()
            b2b_path = f"{REPO_ROOT}/b2b"
            if os.path.isdir(b2b_path):
                existing_slugs = {f.lower() for f in os.listdir(b2b_path)}

            for q in gsc.get('queries', []):
                query = q['query'].lower()
                # Check of we content hebben voor deze query
                query_words = set(query.split())
                has_match = False
                for slug in existing_slugs:
                    slug_words = set(slug.split('-'))
                    if len(query_words & slug_words) >= 2:
                        has_match = True
                        break
                if not has_match and q['impressions'] > 10:
                    gaps.append({
                        'type': 'gsc_gap',
                        'keyword': q['query'],
                        'impressions': q['impressions'],
                        'priority': q['impressions'],  # Meer impressies = hogere prioriteit
                        'reason': f"Query met {q['impressions']} impressies maar geen matching artikel"
                    })
        except:
            pass

    # 2. Analyseer welke tools te weinig content hebben
    brand_targets = {
        'kinsta': 40, 'synthesia': 35, 'invideo': 30,
        'replit': 25, 'bitvavo': 25, 'murf': 25
    }
    b2b_path = f"{REPO_ROOT}/b2b"
    if os.path.isdir(b2b_path):
        for brand, target in brand_targets.items():
            count = sum(1 for f in os.listdir(b2b_path) if f.lower().startswith(brand))
            if count < target:
                gaps.append({
                    'type': 'brand_gap',
                    'keyword': brand,
                    'current': count,
                    'target': target,
                    'priority': (target - count) * 10,
                    'reason': f"{brand.capitalize()}: {count}/{target} artikelen — {target - count} nodig"
                })

    # 3. Standaard high-value topic templates per brand
    high_value_templates = {
        'kinsta': ['kinsta-vs-{competitor}', 'kinsta-{usecase}-hosting', 'kinsta-pricing-{year}'],
        'synthesia': ['synthesia-vs-{competitor}', 'synthesia-{usecase}', 'ai-video-{topic}'],
        'invideo': ['invideo-vs-{competitor}', 'invideo-{usecase}', 'video-editing-{topic}'],
        'replit': ['replit-vs-{competitor}', 'replit-{usecase}', 'online-coding-{topic}'],
        'bitvavo': ['bitvavo-vs-{competitor}', 'bitvavo-{crypto}', 'crypto-trading-{topic}'],
        'murf': ['murf-vs-{competitor}', 'murf-{usecase}', 'ai-voice-{topic}'],
    }

    competitors = {
        'kinsta': ['siteground', 'cloudways', 'wpengine', 'bluehost'],
        'synthesia': ['heygen', 'runway', 'descript', 'pictory'],
        'invideo': ['canva', 'capcut', 'filmora', 'animoto'],
        'replit': ['github-codespaces', 'stackblitz', 'codesandbox', 'gitpod'],
        'bitvavo': ['binance', 'coinbase', 'kraken', 'bybit'],
        'murf': ['elevenlabs', 'play-ht', 'speechify', 'wellsaid'],
    }

    if os.path.isdir(b2b_path):
        existing = {f.lower() for f in os.listdir(b2b_path)}
        for brand, comps in competitors.items():
            for comp in comps:
                slug = f"{brand}-vs-{comp}"
                if slug not in existing:
                    gaps.append({
                        'type': 'comparison',
                        'keyword': f"{brand} vs {comp}",
                        'suggested_slug': slug,
                        'priority': 25,  # Comparison articles convert well
                        'reason': f"Vergelijkingsartikel {brand.capitalize()} vs {comp.capitalize()} mist"
                    })

    # Sorteer op prioriteit
    gaps.sort(key=lambda x: -x.get('priority', 0))
    return gaps[:20]


def suggest_next_articles(n=5):
    """Stel de N meest impactvolle artikelen voor om te schrijven."""
    gaps = analyze_content_gaps()
    suggestions = []

    for gap in gaps[:n]:
        if gap['type'] == 'gsc_gap':
            suggestions.append(f"🎯 [{gap['impressions']} impressies] Schrijf over: '{gap['keyword']}'")
        elif gap['type'] == 'brand_gap':
            suggestions.append(f"📊 {gap['reason']}")
        elif gap['type'] == 'comparison':
            suggestions.append(f"⚔️ {gap['keyword'].title()} — vergelijkingsartikel (hoge conversie)")

    return suggestions


# ── MODULE 6: COMPETITOR DOMINATION ENGINE ─────────────────────────────────
COMPETITORS_FILE = "/root/felix_hq/victor_competitors.json"
CLUSTERS_FILE = "/root/felix_hq/victor_clusters.json"
BATTLES_FILE = "/root/felix_hq/victor_battles.json"

def load_competitor_data():
    if os.path.exists(COMPETITORS_FILE):
        try:
            return json.load(open(COMPETITORS_FILE))
        except:
            pass
    return {"sites": {}, "their_content": [], "our_wins": [], "last_crawl": None}

def save_competitor_data(data):
    data["their_content"] = data.get("their_content", [])[-200:]
    data["our_wins"] = data.get("our_wins", [])[-50:]
    with open(COMPETITORS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_clusters():
    if os.path.exists(CLUSTERS_FILE):
        try:
            return json.load(open(CLUSTERS_FILE))
        except:
            pass
    return {"pillars": {}, "clusters": {}, "internal_links_map": {}}

def save_clusters(data):
    with open(CLUSTERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_battles():
    if os.path.exists(BATTLES_FILE):
        try:
            return json.load(open(BATTLES_FILE))
        except:
            pass
    return {"active": [], "won": [], "lost": []}

def save_battles(data):
    data["won"] = data.get("won", [])[-50:]
    data["lost"] = data.get("lost", [])[-50:]
    with open(BATTLES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# Competitor sites per niche
COMPETITOR_SITES = {
    'kinsta': [
        'https://www.elegantthemes.com/blog/?s=kinsta',
        'https://www.websiteplanet.com/?s=kinsta',
    ],
    'synthesia': [
        'https://www.elegantthemes.com/blog/?s=synthesia',
        'https://zapier.com/blog/?q=synthesia',
    ],
    'invideo': [
        'https://zapier.com/blog/?q=invideo',
    ],
    'replit': [
        'https://dev.to/search?q=replit',
    ],
    'bitvavo': [
        'https://www.bitcoinmagazine.nl/?s=bitvavo',
    ],
    'murf': [
        'https://zapier.com/blog/?q=murf+ai',
    ],
}


def crawl_competitor_page(url, timeout=15):
    """Crawl een pagina en extract titel, headings, en woordcount."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=timeout)
        html = resp.read().decode('utf-8', errors='replace')

        # Extract titles van artikelen op de pagina
        articles = []
        # Zoek naar links met titels
        link_pattern = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{15,120})</a>', html)
        for href, title in link_pattern:
            title = title.strip()
            # Filter op relevante links (skip navigatie, footers etc)
            skip_words = ['menu', 'nav', 'footer', 'cookie', 'privacy', 'login', 'sign', 'cart']
            if any(w in title.lower() for w in skip_words):
                continue
            if any(w in title.lower() for w in ['review', 'vs', 'alternative', 'pricing', 'guide', 'how', 'best', 'top']):
                articles.append({
                    'title': re.sub(r'<[^>]+>', '', title).strip(),
                    'url': href if href.startswith('http') else '',
                    'type': 'review' if 'review' in title.lower()
                            else 'comparison' if 'vs' in title.lower()
                            else 'alternative' if 'alternative' in title.lower()
                            else 'guide'
                })

        return articles[:20]
    except Exception as e:
        log(f"Crawl error {url}: {e}")
        return []


def full_competitor_scan():
    """Scan alle competitor sites en verzamel hun content."""
    comp_data = load_competitor_data()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    all_findings = []

    for brand, urls in COMPETITOR_SITES.items():
        brand_articles = []
        for url in urls:
            articles = crawl_competitor_page(url)
            for art in articles:
                art['brand'] = brand
                art['source_url'] = url
                art['found_at'] = ts
                brand_articles.append(art)

        if brand_articles:
            comp_data["sites"][brand] = {
                "last_scan": ts,
                "article_count": len(brand_articles),
                "types": {}
            }
            for art in brand_articles:
                t = art.get('type', 'other')
                comp_data["sites"][brand]["types"][t] = comp_data["sites"][brand]["types"].get(t, 0) + 1

            all_findings.extend(brand_articles)

    # Sla nieuwe content op (vermijd duplicaten)
    existing_titles = {c.get('title', '').lower() for c in comp_data.get("their_content", [])}
    new_content = [a for a in all_findings if a.get('title', '').lower() not in existing_titles]
    comp_data["their_content"].extend(new_content)
    comp_data["last_crawl"] = ts

    save_competitor_data(comp_data)
    return new_content


def find_skyscraper_targets():
    """Vind competitor artikelen waar wij een beter artikel voor kunnen schrijven."""
    comp_data = load_competitor_data()
    b2b_path = f"{REPO_ROOT}/b2b"
    our_slugs = set()
    if os.path.isdir(b2b_path):
        our_slugs = {f.lower() for f in os.listdir(b2b_path)}

    targets = []
    for article in comp_data.get("their_content", []):
        title = article.get('title', '').lower()
        brand = article.get('brand', '')

        # Maak een slug van hun titel
        potential_slug = re.sub(r'[^a-z0-9\s-]', '', title).strip().replace(' ', '-')[:60]

        # Check of wij al iets vergelijkbaars hebben
        has_similar = False
        title_words = set(title.split())
        for slug in our_slugs:
            slug_words = set(slug.split('-'))
            overlap = len(title_words & slug_words)
            if overlap >= 3:
                has_similar = True
                break

        if not has_similar:
            # Prioriteit op basis van type
            priority = {'comparison': 90, 'alternative': 85, 'review': 70, 'guide': 60}
            targets.append({
                'competitor_title': article.get('title', ''),
                'brand': brand,
                'type': article.get('type', 'guide'),
                'priority': priority.get(article.get('type', 'guide'), 50),
                'suggested_slug': f"{brand}-{potential_slug}"[:70],
                'source': article.get('url', '')
            })

    targets.sort(key=lambda x: -x['priority'])
    return targets[:15]


def write_skyscraper_article(target):
    """Schrijf een artikel dat BETER is dan de concurrent."""
    brand = target['brand'].capitalize()
    if brand.lower() == 'invideo':
        brand = 'InVideo'
    comp_title = target['competitor_title']
    article_type = target['type']
    slug = target['suggested_slug']

    # Bepaal affiliate link
    aff_link = VAULT.get(brand, VAULT.get(brand.capitalize(), ''))

    type_instructions = {
        'comparison': f"""Schrijf een UITGEBREID vergelijkingsartikel. Structuur:
- Intro: welk probleem lossen beide tools op?
- Feature-voor-feature vergelijkingstabel (min 10 features)
- Pricing vergelijking met concrete bedragen
- Echte use cases: wanneer kies je tool A vs B?
- Performance/snelheid vergelijking als relevant
- Pros & cons per tool
- Eindoordeel met duidelijke aanbeveling
- FAQ (5 vragen)""",
        'alternative': f"""Schrijf een UITGEBREID alternatieven-artikel. Structuur:
- Intro: waarom zoeken mensen alternatieven?
- Top 5-7 alternatieven met per alternatief: features, pricing, pros/cons
- Vergelijkingstabel
- Voor wie is welk alternatief het best?
- Onze aanbeveling
- FAQ (5 vragen)""",
        'review': f"""Schrijf een DIEPGAANDE review. Structuur:
- Intro: wat is {brand} en voor wie?
- Hands-on ervaring: wat viel op?
- Alle features in detail (met concrete voorbeelden)
- Pricing breakdown per tier
- Performance tests/resultaten
- Pros & cons (eerlijk)
- Vergelijking met 2-3 concurrenten
- Conclusie: is het de investering waard?
- FAQ (5 vragen)""",
        'guide': f"""Schrijf een COMPLETE how-to guide. Structuur:
- Intro: wat ga je leren?
- Stap-voor-stap uitleg met concrete voorbeelden
- Tips en best practices
- Veelgemaakte fouten
- Geavanceerde technieken
- Conclusie
- FAQ (5 vragen)"""
    }

    prompt = f"""SKYSCRAPER OPDRACHT: Schrijf een artikel dat BETER is dan dit competitor artikel: "{comp_title}"

Brand: {brand}
Type: {article_type}
Affiliate link: {aff_link}

{type_instructions.get(article_type, type_instructions['guide'])}

REGELS:
- Minimaal 2500 woorden
- Meer detail, meer data, meer voorbeelden dan de concurrent
- Concrete cijfers en pricing (geen vage claims)
- Schrijf als een ervaren founder, niet als AI
- HTML content alleen (geen <html>/<head>/<body> tags)
- Interne links naar /b2b/ waar relevant
- rel="nofollow sponsored" op affiliate links"""

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=6000
        )
        content = res.choices[0].message.content.replace("```html", "").replace("```", "").strip()

        # Maak het artikel aan
        article_dir = f"{REPO_ROOT}/b2b/{slug}"
        article_path = f"{article_dir}/index.html"
        os.makedirs(article_dir, exist_ok=True)

        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Restyle met fix_articles.py
        fix_script = "/root/felix_hq/fix_articles.py"
        if os.path.exists(fix_script):
            run_command(f"cd {REPO_ROOT} && python3 {fix_script}", timeout=120)

        return True, slug
    except Exception as e:
        return False, str(e)


def build_topic_clusters():
    """Bouw topical authority clusters: pillar pages + supporting articles."""
    clusters = load_clusters()
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return clusters

    all_articles = [f for f in os.listdir(b2b_path) if os.path.isdir(os.path.join(b2b_path, f))]

    # Definieer pillar topics per brand
    pillar_topics = {
        'kinsta': {
            'pillar': 'kinsta-review',
            'cluster_keywords': ['hosting', 'wordpress', 'performance', 'pricing', 'vs', 'migration', 'speed', 'cdn', 'staging'],
            'display': 'Kinsta Web Hosting'
        },
        'synthesia': {
            'pillar': 'synthesia-review',
            'cluster_keywords': ['ai-video', 'avatar', 'text-to-video', 'vs', 'alternative', 'pricing', 'template', 'enterprise'],
            'display': 'Synthesia AI Video'
        },
        'invideo': {
            'pillar': 'invideo-review',
            'cluster_keywords': ['video-editor', 'template', 'vs', 'alternative', 'pricing', 'tutorial', 'youtube'],
            'display': 'InVideo Video Creation'
        },
        'replit': {
            'pillar': 'replit-review',
            'cluster_keywords': ['coding', 'ide', 'vs', 'alternative', 'ai', 'deploy', 'collaboration', 'pricing'],
            'display': 'Replit Online IDE'
        },
        'bitvavo': {
            'pillar': 'bitvavo-review',
            'cluster_keywords': ['crypto', 'trading', 'vs', 'fees', 'alternative', 'bitcoin', 'staking', 'api'],
            'display': 'Bitvavo Crypto Trading'
        },
        'murf': {
            'pillar': 'murf-review',
            'cluster_keywords': ['voice', 'text-to-speech', 'vs', 'alternative', 'pricing', 'ai-voice', 'voiceover'],
            'display': 'Murf AI Voice'
        },
    }

    for brand, config in pillar_topics.items():
        # Vind alle artikelen in dit cluster
        brand_articles = [a for a in all_articles if a.lower().startswith(brand)]
        cluster_articles = []

        for article in brand_articles:
            relevance = sum(1 for kw in config['cluster_keywords'] if kw in article.lower())
            cluster_articles.append({
                'slug': article,
                'relevance': relevance,
                'is_pillar': article == config['pillar']
            })

        cluster_articles.sort(key=lambda x: (-x['is_pillar'], -x['relevance']))

        clusters["pillars"][brand] = {
            'pillar_slug': config['pillar'],
            'display_name': config['display'],
            'total_articles': len(brand_articles),
            'cluster_size': len(cluster_articles),
            'articles': [a['slug'] for a in cluster_articles]
        }

        # Bouw internal links map: elk artikel linkt naar pillar + 2-3 gerelateerde
        for article in cluster_articles:
            slug = article['slug']
            links_to = []
            # Link naar pillar (als het niet de pillar zelf is)
            if not article['is_pillar'] and config['pillar'] in [a.lower() for a in all_articles]:
                links_to.append(config['pillar'])
            # Link naar 2-3 gerelateerde artikelen
            related = [a['slug'] for a in cluster_articles
                       if a['slug'] != slug and not a['is_pillar']][:3]
            links_to.extend(related)
            clusters["internal_links_map"][slug] = links_to

    save_clusters(clusters)
    return clusters


def apply_cluster_internal_links():
    """Voeg strategische interne links toe op basis van topic clusters."""
    clusters = load_clusters()
    links_map = clusters.get("internal_links_map", {})
    b2b_path = f"{REPO_ROOT}/b2b"
    fixed = 0

    for slug, link_targets in links_map.items():
        article_path = os.path.join(b2b_path, slug, "index.html")
        if not os.path.isfile(article_path):
            continue

        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Skip als er al cluster links zijn
            if 'cluster-links' in html:
                continue

            # Bouw links block
            links_html = ""
            for target in link_targets[:4]:
                display = target.replace('-', ' ').title()
                links_html += f'<li><a href="/b2b/{target}/" style="color:#3b82f6;text-decoration:none;transition:color 0.2s">{display}</a></li>\n'

            if not links_html:
                continue

            # Bepaal pillar info
            brand = slug.split('-')[0].lower()
            pillar_info = clusters.get("pillars", {}).get(brand, {})
            cluster_name = pillar_info.get('display_name', brand.capitalize())

            cluster_block = f"""<div id="cluster-links" style="margin-top:30px;padding:24px;background:linear-gradient(135deg,#1a1f2e,#1e293b);border:1px solid #2d3748;border-radius:12px;">
<h4 style="color:#e6edf3;margin-top:0;font-size:16px;">🔗 Meer over {cluster_name}:</h4>
<ul style="list-style:none;padding:0;margin:0;">{links_html}</ul>
</div>"""

            if '</body>' in html:
                html = html.replace('</body>', f"{cluster_block}\n</body>")
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                fixed += 1
        except:
            pass

    return fixed


def update_ranking_battles():
    """Track ranking battles: vergelijk onze positie vs concurrenten per keyword."""
    if not os.path.exists(GSC_DATA_FILE):
        return []

    try:
        with open(GSC_DATA_FILE) as f:
            gsc = json.load(f)
    except:
        return []

    battles = load_battles()
    ts = datetime.now().strftime('%Y-%m-%d')
    updates = []

    for page in gsc.get('pages', []):
        slug = page['page'].split('/b2b/')[-1].rstrip('/') if '/b2b/' in page['page'] else ''
        if not slug:
            continue

        position = page.get('position', 99)
        clicks = page.get('clicks', 0)
        impressions = page.get('impressions', 0)

        # Check of er al een battle is voor dit slug
        existing = None
        for b in battles.get("active", []):
            if b.get("slug") == slug:
                existing = b
                break

        if existing:
            old_pos = existing.get("best_position", 99)
            existing["current_position"] = position
            existing["clicks"] = clicks
            existing["impressions"] = impressions
            existing["last_check"] = ts

            # Track positie history
            existing.setdefault("position_history", []).append({"date": ts, "pos": position})
            existing["position_history"] = existing["position_history"][-30:]

            if position < old_pos:
                existing["best_position"] = position
                if position <= 3 and old_pos > 3:
                    # TOP 3! Dit is een WIN
                    existing["status"] = "winning"
                    battles["won"].append({
                        "slug": slug, "position": position,
                        "from": old_pos, "date": ts
                    })
                    updates.append(f"🏆 {slug} in TOP {position}! (was #{old_pos})")
                elif position <= 10 and old_pos > 10:
                    updates.append(f"📈 {slug} op PAGINA 1! Positie {position} (was #{old_pos})")

            elif position > old_pos + 5:
                existing["status"] = "declining"
                updates.append(f"📉 {slug} gedaald: #{position} (was #{old_pos}) — actie nodig")
        else:
            # Nieuwe battle
            battles["active"].append({
                "slug": slug,
                "current_position": position,
                "best_position": position,
                "start_position": position,
                "clicks": clicks,
                "impressions": impressions,
                "started_at": ts,
                "last_check": ts,
                "status": "tracking",
                "position_history": [{"date": ts, "pos": position}]
            })

    # Beperk actieve battles tot top 100
    battles["active"] = sorted(battles["active"],
        key=lambda x: x.get("impressions", 0), reverse=True)[:100]

    save_battles(battles)
    return updates


def generate_competitor_report():
    """Volledig competitor intelligence rapport."""
    comp_data = load_competitor_data()
    battles = load_battles()
    clusters = load_clusters()

    report = "🕵️ Competitor Intelligence Report\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Laatste crawl
    report += f"🕐 Laatste scan: {comp_data.get('last_crawl', 'nooit')}\n\n"

    # Per brand: wat hebben concurrenten?
    if comp_data.get("sites"):
        report += "📊 Competitor Content per Brand:\n"
        for brand, info in comp_data["sites"].items():
            types = info.get("types", {})
            type_str = ", ".join(f"{v}x {k}" for k, v in types.items())
            report += f"  {brand.capitalize()}: {info.get('article_count', 0)} artikelen ({type_str})\n"
        report += "\n"

    # Skyscraper targets
    targets = find_skyscraper_targets()
    if targets:
        report += f"🎯 Skyscraper Targets ({len(targets)}):\n"
        for t in targets[:5]:
            report += f"  ⚔️ [{t['type']}] {t['competitor_title'][:60]}\n"
        report += "\n"

    # Ranking battles
    winning = [b for b in battles.get("active", []) if b.get("status") == "winning"]
    declining = [b for b in battles.get("active", []) if b.get("status") == "declining"]
    top10 = [b for b in battles.get("active", []) if b.get("current_position", 99) <= 10]

    report += f"⚔️ Ranking Battles:\n"
    report += f"  Pagina 1: {len(top10)} artikelen\n"
    report += f"  Stijgend: {len(winning)}\n"
    report += f"  Dalend: {len(declining)}\n"
    if battles.get("won"):
        report += f"  🏆 Totaal gewonnen: {len(battles['won'])}\n"
    report += "\n"

    # Topic clusters
    if clusters.get("pillars"):
        report += "🏗️ Topic Clusters:\n"
        for brand, info in clusters["pillars"].items():
            report += f"  {info['display_name']}: {info['total_articles']} artikelen\n"

    return report


def autonomous_competitor_cycle():
    """Dagelijkse autonome competitor cyclus."""
    actions = []
    ts = datetime.now().strftime('%Y-%m-%d')

    # 1. Crawl competitors
    new_content = full_competitor_scan()
    if new_content:
        actions.append(f"Competitor scan: {len(new_content)} nieuwe artikelen gevonden")

    # 2. Update topic clusters
    clusters = build_topic_clusters()
    pillar_count = len(clusters.get("pillars", {}))
    actions.append(f"Topic clusters bijgewerkt: {pillar_count} pillars")

    # 3. Update ranking battles (als GSC data er is)
    battle_updates = update_ranking_battles()
    actions.extend(battle_updates)

    # 4. Vind skyscraper targets
    targets = find_skyscraper_targets()
    if targets:
        actions.append(f"Skyscraper targets: {len(targets)} gevonden")

        # Auto-write het #1 target (1x per week max)
        growth = load_growth_data()
        last_skyscraper = None
        for a in growth.get("growth_actions", []):
            if "skyscraper" in str(a).lower():
                last_skyscraper = a.get("time", "")

        days_since = 999
        if last_skyscraper:
            try:
                last_date = datetime.strptime(last_skyscraper[:10], '%Y-%m-%d')
                days_since = (datetime.now() - last_date).days
            except:
                pass

        if days_since >= 7 and targets:
            top_target = targets[0]
            ok, result = write_skyscraper_article(top_target)
            if ok:
                run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Domination: skyscraper {result}' && git push origin main")
                actions.append(f"🔥 Skyscraper geschreven: {result} (beter dan: {top_target['competitor_title'][:40]})")
                growth["growth_actions"].append({"time": ts, "type": "skyscraper", "slug": result})
                save_growth_data(growth)

    # 5. Apply cluster internal links (1x per week)
    if datetime.now().weekday() == 3:  # Donderdag
        fixed = apply_cluster_internal_links()
        if fixed > 0:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: cluster internal links ({fixed} articles)' && git push origin main")
            actions.append(f"Cluster links: {fixed} artikelen bijgewerkt")

    return actions


# ── MODULE 7: REVENUE INTELLIGENCE ENGINE ──────────────────────────────────
REVENUE_FILE = "/root/felix_hq/victor_revenue.json"
FUNNELS_FILE = "/root/felix_hq/victor_funnels.json"

# Geschatte commissie per tool (conservatief)
COMMISSION_RATES = {
    'kinsta': {'per_signup': 75, 'recurring_monthly': 10, 'currency': '€', 'est_ctr': 0.03},
    'synthesia': {'per_signup': 20, 'recurring_monthly': 0, 'currency': '€', 'est_ctr': 0.025},
    'invideo': {'per_signup': 15, 'recurring_monthly': 0, 'currency': '€', 'est_ctr': 0.02},
    'replit': {'per_signup': 10, 'recurring_monthly': 0, 'currency': '€', 'est_ctr': 0.02},
    'bitvavo': {'per_signup': 5, 'recurring_monthly': 0, 'currency': '€', 'est_ctr': 0.035},
    'murf': {'per_signup': 12, 'recurring_monthly': 0, 'currency': '€', 'est_ctr': 0.02},
}

def load_revenue_data():
    if os.path.exists(REVENUE_FILE):
        try:
            return json.load(open(REVENUE_FILE))
        except:
            pass
    return {"estimates": {}, "daily_snapshots": [], "top_earners": [], "roi_scores": {}}

def save_revenue_data(data):
    data["daily_snapshots"] = data.get("daily_snapshots", [])[-90:]
    data["top_earners"] = data.get("top_earners", [])[-50:]
    with open(REVENUE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_funnels():
    if os.path.exists(FUNNELS_FILE):
        try:
            return json.load(open(FUNNELS_FILE))
        except:
            pass
    return {"funnels": {}, "link_map": {}}

def save_funnels(data):
    with open(FUNNELS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def calculate_article_revenue():
    """Bereken geschatte maandelijkse revenue per artikel op basis van GSC data."""
    if not os.path.exists(GSC_DATA_FILE):
        return {}

    try:
        with open(GSC_DATA_FILE) as f:
            gsc = json.load(f)
    except:
        return {}

    revenue = load_revenue_data()
    estimates = {}

    for page in gsc.get('pages', []):
        slug = page['page'].split('/b2b/')[-1].rstrip('/') if '/b2b/' in page['page'] else ''
        if not slug:
            continue

        brand = slug.split('-')[0].lower()
        if brand == 'invideo':
            brand = 'invideo'

        commission = COMMISSION_RATES.get(brand)
        if not commission:
            continue

        clicks = page.get('clicks', 0)
        impressions = page.get('impressions', 0)
        position = page.get('position', 99)

        # Revenue formule: clicks × affiliate_ctr × commissie
        est_ctr = commission['est_ctr']
        # Positie 1-3 heeft hogere affiliate CTR
        if position <= 3:
            est_ctr *= 1.5
        elif position <= 5:
            est_ctr *= 1.2
        elif position > 20:
            est_ctr *= 0.5

        monthly_signups = clicks * est_ctr
        monthly_revenue = monthly_signups * commission['per_signup']
        recurring = monthly_signups * commission['recurring_monthly'] * 12  # Jaarlijkse recurring

        estimates[slug] = {
            'brand': brand,
            'clicks': clicks,
            'impressions': impressions,
            'position': position,
            'est_monthly_signups': round(monthly_signups, 2),
            'est_monthly_revenue': round(monthly_revenue, 2),
            'est_yearly_recurring': round(recurring, 2),
            'currency': commission['currency'],
            'roi_potential': 'HIGH' if monthly_revenue > 10 else 'MEDIUM' if monthly_revenue > 2 else 'LOW'
        }

    # Sorteer op revenue
    revenue["estimates"] = dict(sorted(estimates.items(), key=lambda x: -x[1]['est_monthly_revenue']))
    revenue["top_earners"] = [
        {"slug": k, "revenue": v['est_monthly_revenue'], "brand": v['brand']}
        for k, v in sorted(estimates.items(), key=lambda x: -x[1]['est_monthly_revenue'])[:20]
    ]

    # Snapshot
    total_monthly = sum(v['est_monthly_revenue'] for v in estimates.values())
    revenue["daily_snapshots"].append({
        "date": datetime.now().strftime('%Y-%m-%d'),
        "total_monthly_estimate": round(total_monthly, 2),
        "article_count": len(estimates),
        "top_brand": max(
            {b: sum(v['est_monthly_revenue'] for v in estimates.values() if v['brand'] == b)
             for b in set(v['brand'] for v in estimates.values())}.items(),
            key=lambda x: x[1]
        )[0] if estimates else 'none'
    })

    save_revenue_data(revenue)
    return estimates


def calculate_roi_scores():
    """Bereken ROI score voor elke mogelijke actie."""
    revenue = load_revenue_data()
    estimates = revenue.get("estimates", {})
    roi = {}

    # 1. Bestaande artikelen verbeteren (hoog impressies, lage positie)
    for slug, data in estimates.items():
        if data['impressions'] > 50 and data['position'] > 5:
            # Als we naar top 3 stijgen: hoeveel extra revenue?
            current_rev = data['est_monthly_revenue']
            potential_clicks = data['impressions'] * 0.10  # ~10% CTR in top 3
            commission = COMMISSION_RATES.get(data['brand'], {})
            potential_rev = potential_clicks * commission.get('est_ctr', 0.02) * commission.get('per_signup', 10)
            uplift = potential_rev - current_rev
            if uplift > 0:
                roi[f"improve_{slug}"] = {
                    'action': f"Verbeter '{slug}' naar top 3",
                    'type': 'improve',
                    'slug': slug,
                    'current_revenue': round(current_rev, 2),
                    'potential_revenue': round(potential_rev, 2),
                    'uplift': round(uplift, 2),
                    'effort_hours': 1,
                    'roi_per_hour': round(uplift, 2),
                    'priority': uplift
                }

    # 2. Nieuwe artikelen schrijven
    gaps = analyze_content_gaps()
    for gap in gaps[:10]:
        brand = gap.get('keyword', '').split('-')[0].split(' ')[0].lower()
        commission = COMMISSION_RATES.get(brand, {})
        if commission:
            # Schat revenue van nieuw artikel
            est_monthly_clicks = 20  # Conservatief voor nieuw artikel
            est_rev = est_monthly_clicks * commission.get('est_ctr', 0.02) * commission.get('per_signup', 10)
            roi[f"write_{gap.get('keyword', '')[:40]}"] = {
                'action': f"Schrijf '{gap.get('keyword', '')}'",
                'type': 'write',
                'potential_revenue': round(est_rev, 2),
                'effort_hours': 0.5,  # Victor schrijft automatisch
                'roi_per_hour': round(est_rev / 0.5, 2),
                'priority': est_rev * (2 if gap.get('type') == 'comparison' else 1)
            }

    # 3. A/B tests op hoge-impressie artikelen
    for slug, data in estimates.items():
        if data['impressions'] > 100 and data['position'] <= 10:
            potential_uplift = data['est_monthly_revenue'] * 0.3  # 30% CTR verbetering
            roi[f"abtest_{slug}"] = {
                'action': f"A/B test titel '{slug}'",
                'type': 'abtest',
                'current_revenue': data['est_monthly_revenue'],
                'potential_uplift': round(potential_uplift, 2),
                'effort_hours': 0.1,
                'roi_per_hour': round(potential_uplift / 0.1, 2),
                'priority': potential_uplift
            }

    # Sorteer op ROI per uur
    revenue["roi_scores"] = dict(sorted(roi.items(), key=lambda x: -x[1].get('roi_per_hour', 0)))
    save_revenue_data(revenue)
    return roi


def build_conversion_funnels():
    """Bouw conversion funnels: awareness → comparison → review → CTA."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return {}

    all_articles = {f.lower(): f for f in os.listdir(b2b_path) if os.path.isdir(os.path.join(b2b_path, f))}
    funnels_data = load_funnels()

    for brand in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
        brand_articles = {k: v for k, v in all_articles.items() if k.startswith(brand)}

        # Categoriseer artikelen per funnel stage
        stages = {
            'awareness': [],    # "what is", "how to", guides
            'consideration': [],  # "vs", "alternatives", "comparison"
            'decision': [],     # "review", "pricing", "best"
        }

        for slug in brand_articles:
            if any(w in slug for w in ['vs', 'alternative', 'comparison', 'vergelijk']):
                stages['consideration'].append(slug)
            elif any(w in slug for w in ['review', 'pricing', 'best', 'top']):
                stages['decision'].append(slug)
            else:
                stages['awareness'].append(slug)

        # Bouw funnel links: awareness → consideration → decision
        funnel = {
            'brand': brand,
            'stages': stages,
            'total': len(brand_articles),
            'gaps': []
        }

        if not stages['consideration']:
            funnel['gaps'].append(f"Geen vergelijkingsartikelen voor {brand.capitalize()}")
        if not stages['decision']:
            funnel['gaps'].append(f"Geen review/pricing artikelen voor {brand.capitalize()}")

        funnels_data["funnels"][brand] = funnel

        # Link map: elk artikel wijst naar de volgende funnel stage
        for slug in stages['awareness']:
            next_stage = stages['consideration'][:2] if stages['consideration'] else stages['decision'][:2]
            funnels_data["link_map"][slug] = next_stage

        for slug in stages['consideration']:
            next_stage = stages['decision'][:2] if stages['decision'] else [f"{brand}-review"]
            funnels_data["link_map"][slug] = next_stage

    save_funnels(funnels_data)
    return funnels_data


def apply_funnel_links():
    """Voeg funnel links toe aan artikelen: leid bezoekers naar conversie."""
    funnels = load_funnels()
    link_map = funnels.get("link_map", {})
    b2b_path = f"{REPO_ROOT}/b2b"
    fixed = 0

    for slug, targets in link_map.items():
        article_path = os.path.join(b2b_path, slug, "index.html")
        if not os.path.isfile(article_path) or not targets:
            continue

        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                html = f.read()

            if 'funnel-links' in html:
                continue

            links = ""
            for target in targets[:3]:
                display = target.replace('-', ' ').title()
                links += f'<a href="/b2b/{target}/" style="display:inline-block;padding:8px 16px;margin:4px;background:#1e293b;color:#3b82f6;border-radius:8px;text-decoration:none;font-size:14px;transition:background 0.2s">{display} →</a>\n'

            funnel_block = f"""<div id="funnel-links" style="margin-top:24px;padding:20px;background:linear-gradient(135deg,#0f1729,#1a1f2e);border:1px solid #2d3748;border-radius:12px;text-align:center;">
<p style="color:#94a3b8;font-size:14px;margin-bottom:12px;">📖 Lees ook:</p>
{links}
</div>"""

            if '</body>' in html:
                html = html.replace('</body>', f"{funnel_block}\n</body>")
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                fixed += 1
        except:
            pass

    return fixed


def generate_revenue_report():
    """Volledig revenue intelligence rapport."""
    estimates = calculate_article_revenue()
    roi = calculate_roi_scores()
    revenue = load_revenue_data()

    report = "💰 Revenue Intelligence Report\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Totaal geschatte revenue
    total = sum(v['est_monthly_revenue'] for v in estimates.values())
    report += f"💶 Geschatte maandelijkse revenue: €{total:.2f}\n"
    report += f"💶 Geschatte jaarlijkse revenue: €{total * 12:.2f}\n\n"

    # Revenue per brand
    brand_totals = {}
    for slug, data in estimates.items():
        b = data['brand']
        brand_totals[b] = brand_totals.get(b, 0) + data['est_monthly_revenue']

    report += "📊 Revenue per Brand:\n"
    for brand, rev in sorted(brand_totals.items(), key=lambda x: -x[1]):
        bar = "█" * max(1, int(rev / max(brand_totals.values()) * 15)) if brand_totals else ""
        report += f"  {brand.capitalize():12s} €{rev:>7.2f}/m {bar}\n"
    report += "\n"

    # Top earners
    top = revenue.get("top_earners", [])[:5]
    if top:
        report += "🏆 Top 5 Artikelen (geschat):\n"
        for i, t in enumerate(top, 1):
            report += f"  {i}. €{t['revenue']:.2f}/m — {t['slug'][:45]}\n"
        report += "\n"

    # Top ROI acties
    top_roi = list(roi.values())[:5]
    if top_roi:
        report += "🎯 Hoogste ROI Acties:\n"
        for r in top_roi:
            report += f"  €{r.get('roi_per_hour', 0):.0f}/uur — {r['action'][:50]}\n"
        report += "\n"

    # Trend
    snapshots = revenue.get("daily_snapshots", [])
    if len(snapshots) >= 2:
        latest = snapshots[-1].get("total_monthly_estimate", 0)
        prev = snapshots[-2].get("total_monthly_estimate", 0)
        diff = latest - prev
        trend = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
        report += f"{trend} Trend: €{diff:+.2f}/maand vs gisteren\n"

    return report


def generate_admin_dashboard():
    """Genereer een live admin dashboard als HTML pagina."""
    revenue = load_revenue_data()
    battles = load_battles()
    growth = load_growth_data()
    ab = load_ab_tests()
    comp_data = load_competitor_data()
    clusters = load_clusters()

    estimates = revenue.get("estimates", {})
    total_monthly = sum(v.get('est_monthly_revenue', 0) for v in estimates.values())
    total_articles = len(estimates)

    # Revenue per brand
    brand_rev = {}
    for slug, data in estimates.items():
        b = data.get('brand', '')
        brand_rev[b] = brand_rev.get(b, 0) + data.get('est_monthly_revenue', 0)

    brand_cards = ""
    brand_colors = {'kinsta': '#8b5cf6', 'synthesia': '#3b82f6', 'invideo': '#a78bfa',
                    'replit': '#f59e0b', 'bitvavo': '#10b981', 'murf': '#ec4899'}

    for brand in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
        rev = brand_rev.get(brand, 0)
        color = brand_colors.get(brand, '#3b82f6')
        count = sum(1 for s, d in estimates.items() if d.get('brand') == brand)
        brand_cards += f"""<div style="background:#1a1f2e;border-radius:12px;padding:20px;border-top:3px solid {color}">
<h3 style="color:{color};margin:0 0 8px 0;font-size:16px">{brand.capitalize()}</h3>
<div style="font-size:28px;font-weight:700;color:#e6edf3">€{rev:.2f}<span style="font-size:14px;color:#64748b">/m</span></div>
<div style="color:#64748b;font-size:13px;margin-top:4px">{count} artikelen</div>
</div>"""

    # Top earners tabel
    top_rows = ""
    for i, (slug, data) in enumerate(list(estimates.items())[:10], 1):
        color = brand_colors.get(data.get('brand', ''), '#3b82f6')
        pos = data.get('position', 99)
        pos_color = '#10b981' if pos <= 3 else '#f59e0b' if pos <= 10 else '#ef4444'
        top_rows += f"""<tr style="border-bottom:1px solid #1e293b">
<td style="padding:10px;color:#64748b">{i}</td>
<td style="padding:10px"><span style="color:{color}">●</span> <span style="color:#e6edf3">{slug[:40]}</span></td>
<td style="padding:10px;color:#e6edf3;font-weight:600">€{data.get('est_monthly_revenue', 0):.2f}</td>
<td style="padding:10px;color:{pos_color}">#{pos:.0f}</td>
<td style="padding:10px;color:#64748b">{data.get('clicks', 0)}</td>
</tr>"""

    # Battles
    top10_count = sum(1 for b in battles.get("active", []) if b.get("current_position", 99) <= 10)
    rising_count = sum(1 for b in battles.get("active", [])
                       if b.get("current_position", 99) < b.get("start_position", 99))
    won_count = len(battles.get("won", []))

    # Revenue snapshots voor chart
    snapshots = revenue.get("daily_snapshots", [])[-30:]
    chart_labels = [s.get('date', '')[5:] for s in snapshots]
    chart_values = [s.get('total_monthly_estimate', 0) for s in snapshots]

    chart_js = ""
    if chart_values:
        max_val = max(chart_values) if chart_values else 1
        bars = ""
        for i, (label, val) in enumerate(zip(chart_labels, chart_values)):
            height = max(4, int(val / max_val * 120))
            bars += f"""<div style="display:flex;flex-direction:column;align-items:center;flex:1;min-width:20px">
<div style="width:100%;max-width:24px;height:{height}px;background:linear-gradient(to top,#3b82f6,#8b5cf6);border-radius:4px 4px 0 0"></div>
<div style="font-size:9px;color:#64748b;margin-top:4px;transform:rotate(-45deg)">{label}</div>
</div>"""
        chart_js = f"""<div style="display:flex;align-items:flex-end;height:160px;gap:2px;padding:10px 0">{bars}</div>"""

    # AB tests
    ab_section = ""
    for test in ab.get("active", []):
        ab_section += f"""<div style="background:#1e293b;padding:12px;border-radius:8px;margin-bottom:8px">
<span style="color:#f59e0b">🔬</span> <span style="color:#e6edf3">{test.get('slug', '')}</span>
<span style="color:#64748b"> — variant {test.get('current_variant', '?').upper()}</span>
</div>"""
    if not ab_section:
        ab_section = '<div style="color:#64748b;padding:12px">Geen actieve tests. Gebruik /abtest om te starten.</div>'

    ts = datetime.now().strftime('%Y-%m-%d %H:%M UTC')

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Victor Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0e17;color:#e6edf3;font-family:'Inter',sans-serif;padding:20px}}
.container{{max-width:1200px;margin:0 auto}}
.header{{text-align:center;padding:30px 0;border-bottom:1px solid #1e293b;margin-bottom:30px}}
.header h1{{font-size:28px;font-weight:800;background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header .subtitle{{color:#64748b;margin-top:8px;font-size:14px}}
.stats-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:30px}}
.stat-card{{background:#1a1f2e;border-radius:12px;padding:20px;text-align:center}}
.stat-card .value{{font-size:32px;font-weight:700;color:#e6edf3}}
.stat-card .label{{color:#64748b;font-size:13px;margin-top:4px}}
.section{{margin-bottom:30px}}
.section h2{{font-size:18px;font-weight:600;margin-bottom:16px;color:#e6edf3;display:flex;align-items:center;gap:8px}}
.brand-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
table{{width:100%;border-collapse:collapse;background:#111827;border-radius:12px;overflow:hidden}}
th{{text-align:left;padding:12px;color:#64748b;font-size:13px;font-weight:500;border-bottom:1px solid #1e293b}}
.chart-container{{background:#111827;border-radius:12px;padding:20px}}
</style>
</head>
<body>
<div class="container">

<div class="header">
<h1>Victor Command Center</h1>
<div class="subtitle">AIBuilder Marketplace — Revenue Intelligence Dashboard</div>
<div style="color:#475569;font-size:12px;margin-top:4px">Laatste update: {ts}</div>
</div>

<div class="stats-row">
<div class="stat-card">
<div class="value" style="color:#10b981">€{total_monthly:.0f}</div>
<div class="label">Geschatte Revenue/maand</div>
</div>
<div class="stat-card">
<div class="value">{total_articles}</div>
<div class="label">Getrackte Artikelen</div>
</div>
<div class="stat-card">
<div class="value" style="color:#3b82f6">{top10_count}</div>
<div class="label">Pagina 1 Rankings</div>
</div>
<div class="stat-card">
<div class="value" style="color:#f59e0b">{rising_count}</div>
<div class="label">Stijgende Artikelen</div>
</div>
<div class="stat-card">
<div class="value" style="color:#8b5cf6">{won_count}</div>
<div class="label">Ranking Battles Gewonnen</div>
</div>
</div>

<div class="section">
<h2>💰 Revenue per Brand</h2>
<div class="brand-grid">{brand_cards}</div>
</div>

<div class="section">
<h2>📈 Revenue Trend (30 dagen)</h2>
<div class="chart-container">{chart_js if chart_js else '<div style="color:#64748b;padding:20px">Nog geen data. Revenue snapshots worden dagelijks genomen.</div>'}</div>
</div>

<div class="section">
<h2>🏆 Top Earning Artikelen</h2>
<table>
<tr><th>#</th><th>Artikel</th><th>€/maand</th><th>Positie</th><th>Clicks</th></tr>
{top_rows if top_rows else '<tr><td colspan="5" style="padding:20px;color:#64748b;text-align:center">Nog geen data. Gebruik /gsc fetch om te starten.</td></tr>'}
</table>
</div>

<div class="section">
<h2>🔬 A/B Tests</h2>
{ab_section}
</div>

<div style="text-align:center;padding:40px 0;color:#475569;font-size:12px">
Victor 11.0 Domination Matrix — Powered by Claude AI<br>
Automatisch bijgewerkt via /dashboard
</div>

</div>
</body>
</html>"""

    return html


def generate_social_content(slug):
    """Genereer social media content van een artikel."""
    article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
    if not os.path.isfile(article_path):
        return None

    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            html = f.read()

        title_match = re.search(r'<title>(.*?)</title>', html)
        title = title_match.group(1) if title_match else slug.replace('-', ' ').title()

        brand = slug.split('-')[0].capitalize()
        if brand.lower() == 'invideo':
            brand = 'InVideo'
        aff_link = VAULT.get(brand, '')
        url = f"https://aibuildermarketplace.com/b2b/{slug}/"

        prompt = f"""Maak social media content voor dit artikel:
Titel: {title}
URL: {url}
Brand: {brand}
Affiliate: {aff_link}

Genereer EXACT dit format:

TWITTER/X:
[Tweet max 280 chars, met emoji, URL, en 2-3 relevante hashtags]

LINKEDIN:
[LinkedIn post, 3-4 zinnen, professioneel maar engaging, met URL]

EMAIL SUBJECT:
[Pakkende email onderwerp regel]

EMAIL SNIPPET:
[2-3 zinnen teaser voor in een newsletter, met CTA naar het artikel]

YOUTUBE SCRIPT INTRO:
[30 seconden intro script voor een video over dit onderwerp, voor Synthesia]"""

        res = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=1000
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


# ── MODULE 8: VICTOR AUTOPILOT ENGINE ──────────────────────────────────────
AUTOPILOT_FILE = "/root/felix_hq/victor_autopilot.json"
SPRINT_FILE = "/root/felix_hq/victor_sprint.json"

def load_autopilot():
    if os.path.exists(AUTOPILOT_FILE):
        try:
            return json.load(open(AUTOPILOT_FILE))
        except:
            pass
    return {"predictions": [], "chains_triggered": [], "recycled": [], "briefings": []}

def save_autopilot(data):
    data["predictions"] = data.get("predictions", [])[-100:]
    data["chains_triggered"] = data.get("chains_triggered", [])[-50:]
    data["recycled"] = data.get("recycled", [])[-50:]
    data["briefings"] = data.get("briefings", [])[-30:]
    with open(AUTOPILOT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_sprint():
    if os.path.exists(SPRINT_FILE):
        try:
            return json.load(open(SPRINT_FILE))
        except:
            pass
    return {"current_week": None, "planned_tasks": [], "completed_tasks": [], "history": []}

def save_sprint(data):
    data["history"] = data.get("history", [])[-12:]
    with open(SPRINT_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def predict_ranking_success(slug_or_keyword, brand):
    """Voorspel de kans dat een artikel op pagina 1 komt."""
    score = 50  # Basis score
    factors = []

    # Factor 1: Historisch succes van dit brand
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc = json.load(f)
            brand_pages = [p for p in gsc.get('pages', [])
                           if brand.lower() in p.get('page', '').lower()]
            if brand_pages:
                avg_pos = sum(p.get('position', 50) for p in brand_pages) / len(brand_pages)
                top10_pct = sum(1 for p in brand_pages if p.get('position', 99) <= 10) / len(brand_pages) * 100
                if top10_pct > 30:
                    score += 15
                    factors.append(f"Brand {brand} rankt goed ({top10_pct:.0f}% pagina 1)")
                elif top10_pct > 10:
                    score += 8
                    factors.append(f"Brand {brand} heeft enige rankings ({top10_pct:.0f}%)")
                else:
                    score -= 5
                    factors.append(f"Brand {brand} rankt moeilijk ({top10_pct:.0f}%)")
        except:
            pass

    # Factor 2: Content type (vergelijkingen en reviews ranken beter)
    keyword = slug_or_keyword.lower()
    if 'vs' in keyword or 'versus' in keyword:
        score += 15
        factors.append("'vs' artikelen ranken goed (laag competition)")
    elif 'alternative' in keyword:
        score += 12
        factors.append("Alternatieven-artikelen hebben goede kans")
    elif 'review' in keyword:
        score += 10
        factors.append("Reviews ranken redelijk")
    elif 'pricing' in keyword or 'kosten' in keyword:
        score += 8
        factors.append("Pricing artikelen trekken kopers")
    elif 'how' in keyword or 'tutorial' in keyword or 'guide' in keyword:
        score += 5
        factors.append("How-to's hebben breed publiek")

    # Factor 3: Concurrentie check (hebben we al vergelijkbare content?)
    b2b_path = f"{REPO_ROOT}/b2b"
    if os.path.isdir(b2b_path):
        existing = os.listdir(b2b_path)
        similar = sum(1 for e in existing if brand.lower() in e.lower())
        if similar > 30:
            score += 10
            factors.append(f"Sterke topical authority ({similar} artikelen)")
        elif similar > 15:
            score += 5
            factors.append(f"Groeiende authority ({similar} artikelen)")
        else:
            score -= 5
            factors.append(f"Weinig authority nog ({similar} artikelen)")

    # Factor 4: Keyword in bestaande GSC queries (er is al vraag)
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc = json.load(f)
            keyword_words = set(keyword.replace('-', ' ').split())
            for q in gsc.get('queries', []):
                query_words = set(q['query'].lower().split())
                if len(keyword_words & query_words) >= 2:
                    score += 10
                    factors.append(f"Keyword al in GSC queries ({q['impressions']} imp)")
                    break
        except:
            pass

    # Factor 5: Commissie waarde (hogere commissie = meer moeite waard)
    commission = COMMISSION_RATES.get(brand.lower(), {})
    if commission.get('per_signup', 0) >= 50:
        score += 10
        factors.append(f"Hoge commissie (€{commission['per_signup']}/signup)")
    elif commission.get('per_signup', 0) >= 15:
        score += 5
        factors.append(f"Gemiddelde commissie (€{commission['per_signup']}/signup)")

    # Cap tussen 5 en 95
    score = max(5, min(95, score))

    # Sla voorspelling op
    autopilot = load_autopilot()
    autopilot["predictions"].append({
        "keyword": slug_or_keyword,
        "brand": brand,
        "score": score,
        "factors": factors,
        "date": datetime.now().strftime('%Y-%m-%d')
    })
    save_autopilot(autopilot)

    return score, factors


def trigger_chain_reaction(slug, event_type="page1"):
    """Trigger een ketting van acties wanneer een artikel een milestone bereikt."""
    autopilot = load_autopilot()
    actions_taken = []
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')

    brand = slug.split('-')[0].lower()
    if brand == 'invideo':
        brand = 'invideo'

    if event_type == "page1":
        # 1. Schrijf 2 supporting cluster artikelen
        clusters = load_clusters()
        pillar = clusters.get("pillars", {}).get(brand, {})
        existing = set(pillar.get("articles", []))

        competitors_for_brand = {
            'kinsta': ['siteground', 'cloudways', 'wpengine'],
            'synthesia': ['heygen', 'runway', 'descript'],
            'invideo': ['canva', 'capcut', 'filmora'],
            'replit': ['github-codespaces', 'stackblitz', 'gitpod'],
            'bitvavo': ['binance', 'coinbase', 'kraken'],
            'murf': ['elevenlabs', 'play-ht', 'speechify'],
        }

        comps = competitors_for_brand.get(brand, [])
        written = 0
        for comp in comps[:2]:
            new_slug = f"{brand}-vs-{comp}"
            if new_slug not in existing and not os.path.exists(f"{REPO_ROOT}/b2b/{new_slug}/index.html"):
                # Voorspel eerst
                pred_score, _ = predict_ranking_success(new_slug, brand)
                if pred_score >= 50:
                    target = {
                        'competitor_title': f"{brand.capitalize()} vs {comp.capitalize()}",
                        'brand': brand,
                        'type': 'comparison',
                        'suggested_slug': new_slug
                    }
                    ok, result = write_skyscraper_article(target)
                    if ok:
                        written += 1
                        actions_taken.append(f"Cluster artikel geschreven: {new_slug} (score: {pred_score}%)")
                if written >= 2:
                    break

        # 2. Genereer social content
        try:
            social = generate_social_content(slug)
            if social:
                actions_taken.append("Social media content gegenereerd")
        except:
            pass

        # 3. Upgrade CTA in het winning artikel
        article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
        if os.path.isfile(article_path):
            try:
                with open(article_path, 'r', encoding='utf-8') as f:
                    html = f.read()

                aff_link = VAULT.get(brand.capitalize(), VAULT.get(brand, ''))
                if aff_link and 'chain-cta' not in html:
                    brand_cap = brand.capitalize()
                    if brand == 'invideo':
                        brand_cap = 'InVideo'
                    cta = f"""<div id="chain-cta" style="margin:30px 0;padding:28px;background:linear-gradient(135deg,#1a1f2e,#0f172a);border:2px solid #3b82f6;border-radius:16px;text-align:center">
<p style="font-size:20px;font-weight:700;color:#e6edf3;margin-bottom:12px">🏆 #{brand_cap} — Lezer Favoriet</p>
<p style="color:#94a3b8;margin-bottom:20px">Dit artikel staat in de TOP van Google. Sluit je aan bij duizenden die al gekozen hebben.</p>
<a href="{aff_link}" rel="nofollow sponsored" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:#fff;border-radius:10px;text-decoration:none;font-weight:600;font-size:16px">Start Gratis met {brand_cap} →</a>
</div>"""
                    if '</body>' in html:
                        html = html.replace('</body>', f"{cta}\n</body>")
                        with open(article_path, 'w', encoding='utf-8') as f:
                            f.write(html)
                        actions_taken.append("Premium CTA toegevoegd aan winning artikel")
            except:
                pass

        # 4. Git push alles
        if actions_taken:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Chain Reaction: {slug} hit page 1' && git push origin main")

    autopilot["chains_triggered"].append({
        "slug": slug, "event": event_type, "actions": actions_taken, "date": ts
    })
    save_autopilot(autopilot)
    return actions_taken


def recycle_old_content():
    """Detecteer en ververs artikelen die oud zijn en dalende rankings hebben."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return []

    battles = load_battles()
    recycled = []
    now = time.time()
    three_months = 90 * 24 * 3600

    # Vind artikelen die oud zijn EN dalende rankings hebben
    declining = {b['slug']: b for b in battles.get("active", []) if b.get("status") == "declining"}

    for folder in os.listdir(b2b_path):
        article_path = os.path.join(b2b_path, folder, "index.html")
        if not os.path.isfile(article_path):
            continue

        mtime = os.path.getmtime(article_path)
        age_days = (now - mtime) / 86400

        # Alleen recyclen als >90 dagen oud EN dalende ranking
        if age_days < 90:
            continue
        if folder not in declining:
            continue

        battle = declining[folder]
        brand = folder.split('-')[0].capitalize()
        if brand.lower() == 'invideo':
            brand = 'InVideo'

        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                old_html = f.read()

            old_size = len(old_html)

            # Herschrijf met Claude
            prompt = f"""Dit artikel over {brand} is {age_days:.0f} dagen oud en daalt in Google (positie {battle.get('current_position', '?')}).
Herschrijf het VOLLEDIG met verse informatie voor 2026.

Slug: {folder}
Huidige grootte: {old_size} bytes

Schrijf minimaal 2000 woorden. Update alle pricing, features, en vergelijkingen naar 2026.
Voeg toe: verse statistieken, nieuwe features, recente reviews.
HTML content alleen (geen <html>/<head>/<body> tags).
Schrijf als een ervaren founder met actuele kennis."""

            res = client.chat.completions.create(
                model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=5000
            )
            new_content = res.choices[0].message.content.replace("```html", "").replace("```", "").strip()

            # Bewaar de head sectie
            if '</head>' in old_html:
                head = old_html.split('</head>')[0] + '</head>'
                new_html = head + '<body>' + new_content + '</body></html>'
            else:
                new_html = new_content

            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(new_html)

            # Restyle
            fix_script = "/root/felix_hq/fix_articles.py"
            if os.path.exists(fix_script):
                run_command(f"cd {REPO_ROOT} && python3 {fix_script}", timeout=120)

            new_size = os.path.getsize(article_path)
            recycled.append(f"{folder}: {old_size//1024}KB → {new_size//1024}KB ({age_days:.0f} dagen oud, was #{battle.get('current_position', '?')})")
            log(f"Recycled: {folder}")
        except Exception as e:
            log(f"Recycle error {folder}: {e}")

        # Max 2 per cyclus (API kosten)
        if len(recycled) >= 2:
            break

    if recycled:
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Autopilot: recycled {len(recycled)} articles' && git push origin main")

    autopilot = load_autopilot()
    autopilot["recycled"].extend([{"article": r, "date": datetime.now().strftime('%Y-%m-%d')} for r in recycled])
    save_autopilot(autopilot)

    return recycled


def plan_weekly_sprint():
    """Maandag: plan de hele week automatisch."""
    sprint = load_sprint()
    week_id = datetime.now().strftime('%Y-W%W')

    if sprint.get("current_week") == week_id:
        return sprint  # Al gepland

    # Archiveer vorige sprint
    if sprint.get("current_week"):
        sprint["history"].append({
            "week": sprint["current_week"],
            "planned": len(sprint.get("planned_tasks", [])),
            "completed": len(sprint.get("completed_tasks", []))
        })

    # Plan nieuwe sprint
    tasks = []

    # 1. ROI-gebaseerde taken
    roi = calculate_roi_scores()
    for key, data in list(roi.items())[:3]:
        tasks.append({
            "task": data['action'],
            "type": data['type'],
            "priority": "HIGH",
            "est_roi": f"€{data.get('roi_per_hour', 0):.0f}/uur",
            "status": "planned"
        })

    # 2. Content recycling check
    battles = load_battles()
    declining = [b for b in battles.get("active", []) if b.get("status") == "declining"]
    if declining:
        tasks.append({
            "task": f"Recycle {min(len(declining), 2)} dalende artikelen",
            "type": "recycle",
            "priority": "MEDIUM",
            "status": "planned"
        })

    # 3. Skyscraper targets
    targets = find_skyscraper_targets()
    if targets:
        target = targets[0]
        pred_score, _ = predict_ranking_success(target['suggested_slug'], target['brand'])
        tasks.append({
            "task": f"Skyscraper: {target['competitor_title'][:50]} (score: {pred_score}%)",
            "type": "skyscraper",
            "priority": "HIGH" if pred_score >= 70 else "MEDIUM",
            "status": "planned"
        })

    # 4. Cluster links updaten
    tasks.append({
        "task": "Topic cluster links bijwerken",
        "type": "clusters",
        "priority": "LOW",
        "status": "planned"
    })

    # 5. Dashboard updaten
    tasks.append({
        "task": "Admin dashboard refreshen",
        "type": "dashboard",
        "priority": "LOW",
        "status": "planned"
    })

    sprint["current_week"] = week_id
    sprint["planned_tasks"] = tasks
    sprint["completed_tasks"] = []
    save_sprint(sprint)

    return sprint


def execute_sprint_tasks():
    """Voer geplande sprint taken uit (1 per cyclus)."""
    sprint = load_sprint()
    if not sprint.get("planned_tasks"):
        return None

    # Pak de eerste niet-uitgevoerde taak
    for task in sprint["planned_tasks"]:
        if task.get("status") != "planned":
            continue

        task["status"] = "running"
        save_sprint(sprint)
        result = None

        try:
            if task["type"] == "recycle":
                recycled = recycle_old_content()
                result = f"Recycled: {len(recycled)} artikelen" if recycled else "Geen artikelen om te recyclen"

            elif task["type"] == "skyscraper":
                targets = find_skyscraper_targets()
                if targets:
                    ok, res = write_skyscraper_article(targets[0])
                    result = f"Skyscraper geschreven: {res}" if ok else f"Mislukt: {res}"
                else:
                    result = "Geen targets"

            elif task["type"] == "clusters":
                clusters = build_topic_clusters()
                fixed = apply_cluster_internal_links()
                if fixed > 0:
                    run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Sprint: cluster links' && git push origin main")
                result = f"Cluster links: {fixed} artikelen"

            elif task["type"] == "dashboard":
                calculate_article_revenue()
                html = generate_admin_dashboard()
                dashboard_dir = f"{REPO_ROOT}/admin"
                os.makedirs(dashboard_dir, exist_ok=True)
                with open(f"{dashboard_dir}/index.html", 'w', encoding='utf-8') as f:
                    f.write(html)
                run_command(f"cd {REPO_ROOT} && git add admin/ && git diff --cached --quiet || git commit -m 'Victor Sprint: dashboard' && git push origin main")
                result = "Dashboard bijgewerkt"

            elif task["type"] == "improve":
                slug = task.get("task", "").split("'")[1] if "'" in task.get("task", "") else ""
                if slug:
                    # Verbeter specifiek artikel
                    article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
                    if os.path.isfile(article_path):
                        with open(article_path, 'r', encoding='utf-8') as f:
                            old = f.read()
                        brand = slug.split('-')[0].capitalize()
                        prompt = f"Herschrijf dit {brand} artikel VOLLEDIG en beter. Min 2000 woorden. HTML alleen.\nSlug: {slug}"
                        res = client.chat.completions.create(
                            model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=5000
                        )
                        new_content = res.choices[0].message.content.replace("```html", "").replace("```", "").strip()
                        with open(article_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        fix_script = "/root/felix_hq/fix_articles.py"
                        if os.path.exists(fix_script):
                            run_command(f"cd {REPO_ROOT} && python3 {fix_script}", timeout=120)
                        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Sprint: improved {slug}' && git push origin main")
                        result = f"Verbeterd: {slug}"

            task["status"] = "done"
            task["result"] = result or "Uitgevoerd"
            sprint["completed_tasks"].append(task)

        except Exception as e:
            task["status"] = "failed"
            task["result"] = str(e)[:100]
            log(f"Sprint task error: {e}")

        save_sprint(sprint)
        return task

    return None


def generate_daily_briefing():
    """Genereer de ochtend briefing voor Daniel."""
    autopilot = load_autopilot()
    revenue = load_revenue_data()
    battles = load_battles()
    sprint = load_sprint()

    briefing = "☀️ Goedemorgen Daniel!\n━━━━━━━━━━━━━━━━━━━━\n\n"

    # Gisteren samenvatting
    snapshots = revenue.get("daily_snapshots", [])
    if len(snapshots) >= 2:
        today = snapshots[-1]
        yesterday = snapshots[-2]
        click_diff = today.get('total_clicks', 0) - yesterday.get('total_clicks', 0)
        rev = today.get('total_monthly_estimate', 0)
        briefing += f"📊 Gisteren:\n"
        briefing += f"  💶 Geschatte revenue: €{rev:.2f}/maand\n"
        if click_diff != 0:
            briefing += f"  🖱️ Clicks: {'+' if click_diff >= 0 else ''}{click_diff}\n"
        briefing += f"  📄 Artikelen: {today.get('article_count', '?')}\n\n"

    # Ranking updates
    winning = [b for b in battles.get("active", [])
               if b.get("current_position", 99) < b.get("start_position", 99)]
    if winning:
        best = min(winning, key=lambda x: x.get("current_position", 99))
        briefing += f"📈 Beste stijger: {best['slug'][:30]} → #{best['current_position']:.0f}\n"

    top3 = [b for b in battles.get("active", []) if b.get("current_position", 99) <= 3]
    if top3:
        briefing += f"🏆 In TOP 3: {len(top3)} artikelen\n"
    briefing += "\n"

    # Chain reactions
    recent_chains = [c for c in autopilot.get("chains_triggered", [])
                     if c.get("date", "")[:10] == (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')]
    if recent_chains:
        briefing += f"⚡ Chain reactions gisteren: {len(recent_chains)}\n"
        for c in recent_chains[:2]:
            briefing += f"  - {c['slug']}: {len(c.get('actions', []))} acties\n"
        briefing += "\n"

    # Vandaag ga ik...
    briefing += "📋 Vandaag ga ik:\n"
    if sprint.get("planned_tasks"):
        pending = [t for t in sprint["planned_tasks"] if t.get("status") == "planned"]
        for t in pending[:3]:
            icon = "🔴" if t.get("priority") == "HIGH" else "🟡" if t.get("priority") == "MEDIUM" else "⚪"
            briefing += f"  {icon} {t['task'][:55]}\n"
    else:
        briefing += "  Sprint plannen voor deze week\n"

    # Sprint voortgang
    if sprint.get("planned_tasks"):
        total = len(sprint["planned_tasks"])
        done = sum(1 for t in sprint["planned_tasks"] if t.get("status") == "done")
        briefing += f"\n📊 Sprint: {done}/{total} taken klaar"

    autopilot["briefings"].append({"date": datetime.now().strftime('%Y-%m-%d'), "briefing": briefing[:500]})
    save_autopilot(autopilot)

    return briefing


def autopilot_cycle():
    """De complete autopilot cyclus: predict → chain → recycle → sprint → brief."""
    actions = []

    # 1. Check for chain reaction triggers (artikelen die net pagina 1 bereikten)
    battles = load_battles()
    autopilot = load_autopilot()
    triggered_slugs = {c['slug'] for c in autopilot.get("chains_triggered", [])}

    for battle in battles.get("active", []):
        slug = battle.get("slug", "")
        pos = battle.get("current_position", 99)
        start_pos = battle.get("start_position", 99)

        # Chain reaction als: net pagina 1 bereikt EN nog niet getriggered
        if pos <= 10 and start_pos > 10 and slug not in triggered_slugs:
            chain_actions = trigger_chain_reaction(slug, "page1")
            if chain_actions:
                actions.append(f"⚡ Chain reaction voor {slug}: {len(chain_actions)} acties")
                try:
                    bot.send_message(ADMIN_ID,
                        f"⚡ Chain Reaction Triggered!\n\n"
                        f"📄 {slug} bereikt PAGINA 1 (#{pos:.0f})!\n\n"
                        f"Automatische acties:\n" +
                        "\n".join(f"  ✅ {a}" for a in chain_actions))
                except:
                    pass

    # 2. Execute sprint task (1 per cyclus)
    task = execute_sprint_tasks()
    if task:
        actions.append(f"Sprint: {task.get('task', '')[:40]} → {task.get('result', '')[:40]}")

    # 3. Content recycling (alleen als het dinsdag of vrijdag is)
    if datetime.now().weekday() in [1, 4]:
        recycled = recycle_old_content()
        if recycled:
            actions.append(f"Recycled: {len(recycled)} artikelen")

    return actions


# ── MODULE 9: AUTONOMOUS GROWTH ENGINE ─────────────────────────────────────
GROWTH_FILE = "/root/felix_hq/victor_growth.json"
AB_TESTS_FILE = "/root/felix_hq/victor_ab_tests.json"

def load_growth_data():
    if os.path.exists(GROWTH_FILE):
        try:
            return json.load(open(GROWTH_FILE))
        except:
            pass
    return {"daily_snapshots": [], "winning_patterns": [], "growth_actions": []}

def save_growth_data(data):
    data["daily_snapshots"] = data.get("daily_snapshots", [])[-90:]  # 3 maanden history
    data["winning_patterns"] = data.get("winning_patterns", [])[-50:]
    data["growth_actions"] = data.get("growth_actions", [])[-100:]
    with open(GROWTH_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_ab_tests():
    if os.path.exists(AB_TESTS_FILE):
        try:
            return json.load(open(AB_TESTS_FILE))
        except:
            pass
    return {"active": [], "completed": [], "learnings": []}

def save_ab_tests(data):
    data["completed"] = data.get("completed", [])[-30:]
    data["learnings"] = data.get("learnings", [])[-20:]
    with open(AB_TESTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def take_growth_snapshot():
    """Neem een dagelijks snapshot van alle key metrics."""
    growth = load_growth_data()
    ts = datetime.now().strftime('%Y-%m-%d')

    # Check of we vandaag al een snapshot hebben
    if growth["daily_snapshots"] and growth["daily_snapshots"][-1].get("date") == ts:
        return None  # Al gedaan

    snapshot = {"date": ts}

    # Artikel stats
    b2b_path = f"{REPO_ROOT}/b2b"
    if os.path.isdir(b2b_path):
        folders = [f for f in os.listdir(b2b_path) if os.path.isdir(os.path.join(b2b_path, f))]
        snapshot["total_articles"] = len(folders)
        snapshot["per_brand"] = {}
        for brand in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
            snapshot["per_brand"][brand] = sum(1 for f in folders if f.lower().startswith(brand))

        # Gemiddelde artikel grootte
        sizes = []
        for f in folders:
            p = os.path.join(b2b_path, f, "index.html")
            if os.path.isfile(p):
                sizes.append(os.path.getsize(p))
        snapshot["avg_article_size"] = sum(sizes) // len(sizes) if sizes else 0
        snapshot["smallest_article"] = min(sizes) if sizes else 0

    # GSC data als beschikbaar
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc = json.load(f)
            total_clicks = sum(p.get('clicks', 0) for p in gsc.get('pages', []))
            total_impressions = sum(p.get('impressions', 0) for p in gsc.get('pages', []))
            avg_position = 0
            positions = [p['position'] for p in gsc.get('pages', []) if p.get('position')]
            if positions:
                avg_position = round(sum(positions) / len(positions), 1)
            snapshot["total_clicks"] = total_clicks
            snapshot["total_impressions"] = total_impressions
            snapshot["avg_position"] = avg_position
            snapshot["top_page"] = gsc['pages'][0]['page'].split('/')[-2] if gsc.get('pages') else "n/a"
        except:
            pass

    growth["daily_snapshots"].append(snapshot)
    save_growth_data(growth)
    return snapshot


def analyze_growth_trends():
    """Analyseer groeitrends over de laatste 7/30 dagen."""
    growth = load_growth_data()
    snapshots = growth.get("daily_snapshots", [])

    if len(snapshots) < 2:
        return "Nog niet genoeg data. Snapshots worden dagelijks genomen."

    latest = snapshots[-1]
    report = "📈 Growth Trends\n━━━━━━━━━━━━━━━━━━━━\n\n"

    # Vergelijk met 7 dagen geleden
    week_ago = None
    for s in reversed(snapshots[:-1]):
        try:
            s_date = datetime.strptime(s['date'], '%Y-%m-%d')
            l_date = datetime.strptime(latest['date'], '%Y-%m-%d')
            if (l_date - s_date).days >= 6:
                week_ago = s
                break
        except:
            continue

    report += f"📊 Vandaag: {latest.get('total_articles', '?')} artikelen\n"

    if week_ago:
        article_growth = latest.get('total_articles', 0) - week_ago.get('total_articles', 0)
        report += f"📈 Week groei: +{article_growth} artikelen\n"

        if 'total_clicks' in latest and 'total_clicks' in week_ago:
            click_growth = latest['total_clicks'] - week_ago['total_clicks']
            imp_growth = latest.get('total_impressions', 0) - week_ago.get('total_impressions', 0)
            report += f"🖱️ Clicks: {latest['total_clicks']} ({'+' if click_growth >= 0 else ''}{click_growth})\n"
            report += f"👁️ Impressies: {latest['total_impressions']} ({'+' if imp_growth >= 0 else ''}{imp_growth})\n"
            report += f"📍 Gem. positie: {latest.get('avg_position', '?')}\n"

    # Vergelijk met 30 dagen geleden
    month_ago = None
    for s in reversed(snapshots[:-1]):
        try:
            s_date = datetime.strptime(s['date'], '%Y-%m-%d')
            l_date = datetime.strptime(latest['date'], '%Y-%m-%d')
            if (l_date - s_date).days >= 28:
                month_ago = s
                break
        except:
            continue

    if month_ago:
        month_articles = latest.get('total_articles', 0) - month_ago.get('total_articles', 0)
        report += f"\n📅 Maand groei: +{month_articles} artikelen\n"
        if 'total_clicks' in latest and 'total_clicks' in month_ago:
            month_clicks = latest['total_clicks'] - month_ago['total_clicks']
            report += f"🖱️ Click groei (30d): {'+' if month_clicks >= 0 else ''}{month_clicks}\n"

    return report


def identify_winning_patterns():
    """Analyseer GSC data om te bepalen welke content het best presteert."""
    if not os.path.exists(GSC_DATA_FILE):
        return []

    try:
        with open(GSC_DATA_FILE) as f:
            gsc = json.load(f)
    except:
        return []

    growth = load_growth_data()
    patterns = []

    top_pages = sorted(gsc.get('pages', []), key=lambda x: -x.get('clicks', 0))[:20]

    # Analyseer wat top-pagina's gemeen hebben
    brand_performance = {}
    for p in top_pages:
        url = p['page']
        slug = url.split('/b2b/')[-1].rstrip('/') if '/b2b/' in url else ''
        if not slug:
            continue

        brand = slug.split('-')[0].lower()
        if brand not in brand_performance:
            brand_performance[brand] = {'clicks': 0, 'impressions': 0, 'count': 0, 'slugs': []}
        brand_performance[brand]['clicks'] += p.get('clicks', 0)
        brand_performance[brand]['impressions'] += p.get('impressions', 0)
        brand_performance[brand]['count'] += 1
        brand_performance[brand]['slugs'].append(slug)

    # Welk brand presteert het best per artikel?
    for brand, data in sorted(brand_performance.items(), key=lambda x: -x[1]['clicks']):
        if data['count'] > 0:
            avg_clicks = data['clicks'] / data['count']
            patterns.append({
                'type': 'brand_winner',
                'brand': brand,
                'avg_clicks': round(avg_clicks, 1),
                'total_clicks': data['clicks'],
                'top_slugs': data['slugs'][:3],
                'insight': f"{brand.capitalize()}: {avg_clicks:.0f} clicks/artikel gemiddeld"
            })

    # Welke title-patronen werken? (vs, review, pricing, how-to)
    pattern_types = {'vs': [], 'review': [], 'pricing': [], 'how': [], 'best': [], 'alternative': []}
    for p in gsc.get('pages', []):
        slug = p['page'].split('/b2b/')[-1].rstrip('/') if '/b2b/' in p['page'] else ''
        for pt in pattern_types:
            if pt in slug.lower():
                pattern_types[pt].append(p.get('clicks', 0))

    for pt, clicks_list in pattern_types.items():
        if clicks_list:
            avg = sum(clicks_list) / len(clicks_list)
            patterns.append({
                'type': 'content_pattern',
                'pattern': pt,
                'avg_clicks': round(avg, 1),
                'count': len(clicks_list),
                'insight': f"'{pt}' artikelen: gem. {avg:.0f} clicks ({len(clicks_list)} artikelen)"
            })

    # Sla winning patterns op
    growth["winning_patterns"] = patterns
    save_growth_data(growth)

    return patterns


def create_ab_test(slug, variant_a_title, variant_b_title):
    """Start een A/B test op een artikel titel."""
    ab = load_ab_tests()

    # Check of er al een test loopt voor dit artikel
    for test in ab.get("active", []):
        if test.get("slug") == slug:
            return None, f"Er loopt al een A/B test voor {slug}"

    test = {
        "id": f"ab_{slug}_{datetime.now().strftime('%Y%m%d')}",
        "slug": slug,
        "variant_a": {"title": variant_a_title, "days_active": 0, "clicks": 0, "impressions": 0},
        "variant_b": {"title": variant_b_title, "days_active": 0, "clicks": 0, "impressions": 0},
        "current_variant": "a",
        "started_at": datetime.now().strftime('%Y-%m-%d'),
        "switch_every_days": 3,
        "min_impressions": 50,
        "status": "running"
    }

    # Zet variant A live
    article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
    if os.path.isfile(article_path):
        _set_article_title(article_path, variant_a_title)
        ab["active"].append(test)
        save_ab_tests(ab)
        return test, None
    else:
        return None, f"Artikel {slug} niet gevonden"


def _set_article_title(article_path, new_title):
    """Verander de title en h1 van een artikel."""
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Update <title>
        html = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', html)
        # Update eerste <h1>
        html = re.sub(r'<h1[^>]*>.*?</h1>', f'<h1>{new_title}</h1>', html, count=1)
        # Update og:title
        html = re.sub(r'content="[^"]*"(\s*(?:/>|>)\s*<!--\s*og:title)', f'content="{new_title}"\\1', html)
        html = re.sub(r'(property="og:title"\s+content=")[^"]*"', f'\\1{new_title}"', html)

        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    except:
        return False


def check_ab_tests():
    """Check alle actieve A/B tests en wissel varianten als nodig."""
    ab = load_ab_tests()
    if not ab.get("active"):
        return []

    actions = []
    now = datetime.now()

    for test in ab["active"][:]:  # Copy list to allow removal
        slug = test["slug"]
        started = datetime.strptime(test["started_at"], '%Y-%m-%d')
        days_running = (now - started).days
        switch_days = test.get("switch_every_days", 3)
        current = test["current_variant"]

        # Haal GSC data voor dit artikel
        if os.path.exists(GSC_DATA_FILE):
            try:
                with open(GSC_DATA_FILE) as f:
                    gsc = json.load(f)
                for p in gsc.get('pages', []):
                    if slug in p.get('page', ''):
                        variant_key = f"variant_{current}"
                        test[variant_key]["clicks"] = p.get('clicks', 0)
                        test[variant_key]["impressions"] = p.get('impressions', 0)
                        test[variant_key]["days_active"] += 1
                        break
            except:
                pass

        # Wissel variant als het tijd is
        if days_running > 0 and days_running % switch_days == 0:
            new_variant = "b" if current == "a" else "a"
            new_title = test[f"variant_{new_variant}"]["title"]
            article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
            if _set_article_title(article_path, new_title):
                test["current_variant"] = new_variant
                actions.append(f"🔄 {slug}: switched naar variant {new_variant.upper()}")

        # Bepaal winnaar na voldoende data
        min_imp = test.get("min_impressions", 50)
        a = test["variant_a"]
        b = test["variant_b"]

        if a.get("impressions", 0) >= min_imp and b.get("impressions", 0) >= min_imp:
            ctr_a = (a["clicks"] / a["impressions"] * 100) if a["impressions"] > 0 else 0
            ctr_b = (b["clicks"] / b["impressions"] * 100) if b["impressions"] > 0 else 0

            winner = "a" if ctr_a >= ctr_b else "b"
            winner_data = test[f"variant_{winner}"]
            loser = "b" if winner == "a" else "a"
            loser_data = test[f"variant_{loser}"]

            # Pas winnende titel toe
            article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
            _set_article_title(article_path, winner_data["title"])

            # Sla learning op
            winner_ctr = (winner_data["clicks"] / winner_data["impressions"] * 100) if winner_data["impressions"] > 0 else 0
            loser_ctr = (loser_data["clicks"] / loser_data["impressions"] * 100) if loser_data["impressions"] > 0 else 0

            learning = {
                "slug": slug,
                "winner_title": winner_data["title"],
                "loser_title": loser_data["title"],
                "winner_ctr": round(winner_ctr, 2),
                "loser_ctr": round(loser_ctr, 2),
                "improvement": round(winner_ctr - loser_ctr, 2),
                "date": now.strftime('%Y-%m-%d')
            }
            ab["learnings"].append(learning)

            # Verplaats naar completed
            test["status"] = "completed"
            test["winner"] = winner
            ab["completed"].append(test)
            ab["active"].remove(test)

            actions.append(f"🏆 A/B test klaar: {slug} — Variant {winner.upper()} wint! CTR {winner_ctr:.1f}% vs {loser_ctr:.1f}%")

    save_ab_tests(ab)
    return actions


def smart_article_planner():
    """Data-driven planning: welke artikelen schrijven voor maximale groei."""
    plan = []
    growth = load_growth_data()
    patterns = growth.get("winning_patterns", [])

    # 1. Welk brand presteert het best? → schrijf daar meer van
    brand_winners = [p for p in patterns if p['type'] == 'brand_winner']
    brand_winners.sort(key=lambda x: -x.get('avg_clicks', 0))

    if brand_winners:
        top_brand = brand_winners[0]['brand']
        plan.append({
            'priority': 'HIGH',
            'action': f"Schrijf meer {top_brand.capitalize()} artikelen — beste performer ({brand_winners[0]['avg_clicks']} clicks/artikel)",
            'brand': top_brand
        })

    # 2. Welk content-type werkt? → meer daarvan
    content_winners = [p for p in patterns if p['type'] == 'content_pattern']
    content_winners.sort(key=lambda x: -x.get('avg_clicks', 0))

    if content_winners:
        top_pattern = content_winners[0]['pattern']
        plan.append({
            'priority': 'HIGH',
            'action': f"Focus op '{top_pattern}' artikelen — gem. {content_winners[0]['avg_clicks']} clicks",
            'pattern': top_pattern
        })

    # 3. Content gaps uit GSC
    gaps = analyze_content_gaps()
    gsc_gaps = [g for g in gaps if g['type'] == 'gsc_gap'][:3]
    for gap in gsc_gaps:
        plan.append({
            'priority': 'MEDIUM',
            'action': f"Nieuw artikel voor '{gap['keyword']}' ({gap['impressions']} impressies, geen content)",
            'keyword': gap['keyword']
        })

    # 4. Vergelijkingsartikelen (hoge conversie)
    comparison_gaps = [g for g in gaps if g['type'] == 'comparison'][:3]
    for gap in comparison_gaps:
        plan.append({
            'priority': 'MEDIUM',
            'action': f"VS artikel: {gap['keyword']} (vergelijkingen converteren goed)",
            'slug': gap.get('suggested_slug', '')
        })

    # 5. A/B test suggesties voor bestaande artikelen
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc = json.load(f)
            # Artikelen met veel impressies maar lage CTR → A/B test kandidaten
            for p in gsc.get('pages', []):
                if p.get('impressions', 0) > 100 and p.get('ctr', 0) < 2.0:
                    slug = p['page'].split('/b2b/')[-1].rstrip('/')
                    if slug and '/' not in slug:
                        plan.append({
                            'priority': 'MEDIUM',
                            'action': f"A/B test titel van '{slug}' — {p['impressions']} imp maar {p['ctr']}% CTR",
                            'slug': slug
                        })
                        break  # Max 1 A/B test suggestie
        except:
            pass

    return plan


def generate_growth_report():
    """Volledig dagelijks groeirapport met trends, winnaars, en acties."""
    report = "🚀 Victor Growth Report\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # 1. Snapshot
    snapshot = take_growth_snapshot()
    if snapshot:
        report += f"📊 Snapshot: {snapshot.get('total_articles', '?')} artikelen\n"
        if 'total_clicks' in snapshot:
            report += f"🖱️ Clicks: {snapshot['total_clicks']} | Impressies: {snapshot['total_impressions']}\n"
            report += f"📍 Gem. positie: {snapshot.get('avg_position', '?')}\n"
        report += "\n"

    # 2. Trends
    trends = analyze_growth_trends()
    if isinstance(trends, str) and "Nog niet" not in trends:
        report += trends + "\n"

    # 3. Winning patterns
    patterns = identify_winning_patterns()
    if patterns:
        report += "🏆 Top Performers:\n"
        for p in patterns[:5]:
            report += f"  - {p['insight']}\n"
        report += "\n"

    # 4. A/B tests
    ab = load_ab_tests()
    if ab.get("active"):
        report += f"🔬 Actieve A/B tests: {len(ab['active'])}\n"
        for test in ab["active"]:
            report += f"  - {test['slug']}: variant {test['current_variant'].upper()} actief\n"
        report += "\n"

    if ab.get("learnings") and ab["learnings"][-1:]:
        latest = ab["learnings"][-1]
        report += f"💡 Laatste A/B learning: '{latest['winner_title'][:40]}' wint met {latest['improvement']}% meer CTR\n\n"

    # 5. Actieplan
    plan = smart_article_planner()
    if plan:
        report += "📋 Actieplan (data-driven):\n"
        for item in plan[:5]:
            icon = "🔴" if item['priority'] == 'HIGH' else "🟡"
            report += f"  {icon} {item['action']}\n"

    return report


def autonomous_growth_cycle():
    """De kern van de growth engine: analyseer → plan → schrijf → meet → herhaal."""
    actions_taken = []
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 1. Neem een snapshot
    snapshot = take_growth_snapshot()
    if snapshot:
        actions_taken.append(f"Snapshot genomen: {snapshot.get('total_articles', '?')} artikelen")

    # 2. Ververs GSC data (als credentials aanwezig)
    if os.path.exists(GSC_CREDENTIALS):
        try:
            data, err = fetch_gsc_data()
            if data:
                actions_taken.append(f"GSC data vernieuwd: {len(data.get('pages', []))} pagina's")
        except:
            pass

    # 3. Analyseer winnaars
    patterns = identify_winning_patterns()
    if patterns:
        actions_taken.append(f"Winning patterns: {len(patterns)} gevonden")

    # 4. Check A/B tests
    ab_actions = check_ab_tests()
    actions_taken.extend(ab_actions)

    # 5. Rebuild sitemap
    try:
        count = rebuild_sitemap()
        rebuild_robots_txt()
        actions_taken.append(f"Sitemap rebuild: {count} URLs")
    except:
        pass

    # 6. Smart planning
    plan = smart_article_planner()
    if plan:
        # Sla het plan op zodat Victor het kan gebruiken
        growth = load_growth_data()
        growth["growth_actions"].append({
            "time": ts,
            "plan": [p['action'] for p in plan[:5]],
            "patterns_used": len(patterns)
        })
        save_growth_data(growth)
        actions_taken.append(f"Growth plan bijgewerkt: {len(plan)} acties")

    # 7. Auto-write: schrijf het #1 gesuggereerde artikel als het een comparison is
    if plan:
        top = plan[0]
        if top.get('slug') and 'vs' in top.get('slug', ''):
            slug = top['slug']
            article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
            if not os.path.exists(article_path):
                try:
                    brand = slug.split('-')[0].capitalize()
                    competitor = slug.split('-vs-')[-1].replace('-', ' ').title() if '-vs-' in slug else ''
                    prompt = f"""Schrijf een uitgebreid vergelijkingsartikel: {brand} vs {competitor}.
Minimaal 2000 woorden HTML. Structuur: intro, feature vergelijking (tabel), pricing, use cases, pros/cons per tool, verdict, FAQ.
Eerlijk en objectief. Affiliate link voor {brand}: {VAULT.get(brand, VAULT.get(brand.capitalize(), ''))}
Schrijf als een ervaren founder. Geen <html>/<head>/<body> tags, alleen de content HTML."""

                    res = client.chat.completions.create(
                        model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=4000
                    )
                    new_content = res.choices[0].message.content.replace("```html", "").replace("```", "").strip()

                    os.makedirs(os.path.dirname(article_path), exist_ok=True)
                    with open(article_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    # Restyle met fix_articles.py als beschikbaar
                    fix_script = "/root/felix_hq/fix_articles.py"
                    if os.path.exists(fix_script):
                        run_command(f"cd {REPO_ROOT} && python3 {fix_script}", timeout=120)

                    run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Growth: auto-wrote {slug}' && git push origin main")
                    actions_taken.append(f"Auto-geschreven: {slug} (data-driven!)")
                except Exception as e:
                    log(f"Growth auto-write error: {e}")

    # Git push alle wijzigingen
    run_command(f"cd {REPO_ROOT} && git add -A && git diff --cached --quiet || git commit -m 'Victor Growth: daily cycle' && git push origin main")

    return actions_taken


def log(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {text}\n")

# ── COMMAND EXECUTION ───────────────────────────────────────────────────────
def run_command(cmd, timeout=60):
    """Voer bash-commando uit met timeout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:/root/felix_hq/venv/bin"}
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        out = stdout if stdout else stderr if stderr else "(geen output)"
        return out[:3500]
    except subprocess.TimeoutExpired:
        return f"⏱ Timeout na {timeout}s. Commando draait mogelijk nog op de achtergrond."
    except Exception as e:
        return f"❌ Error: {e}"

# ── VICTOR LLM ──────────────────────────────────────────────────────────────
def ask_victor(user_input, history):
    long_ctx = get_long_memory_context()
    full_prompt = SYSTEM_PROMPT
    if long_ctx:
        full_prompt += f"\n\n## LONG-TERM MEMORY\n{long_ctx}"

    messages = [{"role": "system", "content": full_prompt}]
    messages += history[-14:]
    messages.append({"role": "user", "content": user_input})

    try:
        res = client.chat.completions.create(
            model=MODEL, messages=messages, max_tokens=2048, temperature=0.2,
        )
        reply = res.choices[0].message.content.strip()
        extract_learnings(user_input, reply)
        return reply
    except Exception as e:
        log(f"LLM error ({MODEL}): {e}")
        # Fallback naar lokale Ollama
        try:
            fallback = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            res = fallback.chat.completions.create(
                model="gemma4", messages=messages, max_tokens=1024,
            )
            return res.choices[0].message.content.strip()
        except Exception as e2:
            return f"❌ Beide LLMs onbereikbaar. OpenRouter: {e} | Ollama: {e2}"


def ask_victor_with_image(user_text, image_base64, mime_type, history):
    """Stuur een vraag met afbeelding naar Victor (Claude vision)."""
    long_ctx = get_long_memory_context()
    full_prompt = SYSTEM_PROMPT
    if long_ctx:
        full_prompt += f"\n\n## LONG-TERM MEMORY\n{long_ctx}"

    messages = [{"role": "system", "content": full_prompt}]
    messages += history[-14:]

    # Multimodal message: tekst + afbeelding
    content = []
    if user_text:
        content.append({"type": "text", "text": user_text})
    content.append({
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
    })
    messages.append({"role": "user", "content": content})

    try:
        res = client.chat.completions.create(
            model=MODEL, messages=messages, max_tokens=2048, temperature=0.2,
        )
        reply = res.choices[0].message.content.strip()
        extract_learnings(user_text or "[afbeelding]", reply)
        return reply
    except Exception as e:
        log(f"Vision error: {e}")
        return f"❌ Kon afbeelding niet analyseren: {e}"


def download_telegram_file(file_id):
    """Download een bestand van Telegram en retourneer (bytes, file_path)."""
    try:
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        return downloaded, file_info.file_path
    except Exception as e:
        log(f"Download error: {e}")
        return None, None

# ── MODULE 10: DOMINATION MATRIX ENGINE ─────────────────────────────────────
PROGRAMMATIC_FILE = "/root/felix_hq/victor_programmatic.json"
SCHEMA_FILE = "/root/felix_hq/victor_schema.json"
SYNDICATION_FILE = "/root/felix_hq/victor_syndication.json"
LINKGRAPH_FILE = "/root/felix_hq/victor_linkgraph.json"
SERP_FILE = "/root/felix_hq/victor_serp.json"

def load_programmatic():
    if os.path.exists(PROGRAMMATIC_FILE):
        try:
            return json.load(open(PROGRAMMATIC_FILE))
        except:
            pass
    return {"generated_pages": [], "templates": [], "stats": {}}

def save_programmatic(data):
    data["generated_pages"] = data.get("generated_pages", [])[-500:]
    with open(PROGRAMMATIC_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_schema_data():
    if os.path.exists(SCHEMA_FILE):
        try:
            return json.load(open(SCHEMA_FILE))
        except:
            pass
    return {"articles_with_schema": [], "schema_types": {}, "stats": {}}

def save_schema_data(data):
    with open(SCHEMA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_syndication():
    if os.path.exists(SYNDICATION_FILE):
        try:
            return json.load(open(SYNDICATION_FILE))
        except:
            pass
    return {"syndicated": [], "platforms": {}, "backlinks_gained": []}

def save_syndication(data):
    data["syndicated"] = data.get("syndicated", [])[-200:]
    with open(SYNDICATION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_linkgraph():
    if os.path.exists(LINKGRAPH_FILE):
        try:
            return json.load(open(LINKGRAPH_FILE))
        except:
            pass
    return {"pages": {}, "link_scores": {}, "recommendations": [], "last_scan": None}

def save_linkgraph(data):
    data["recommendations"] = data.get("recommendations", [])[-100:]
    with open(LINKGRAPH_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_serp_data():
    if os.path.exists(SERP_FILE):
        try:
            return json.load(open(SERP_FILE))
        except:
            pass
    return {"tracking": {}, "alerts": [], "history": [], "daily_snapshots": []}

def save_serp_data(data):
    data["alerts"] = data.get("alerts", [])[-100:]
    data["history"] = data.get("history", [])[-90:]
    data["daily_snapshots"] = data.get("daily_snapshots", [])[-90:]
    with open(SERP_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ── 10A: PROGRAMMATIC SEO ENGINE ──────────────────────────────────────────

# Template types voor mass page generation
PROGRAMMATIC_TEMPLATES = {
    "vs": {
        "pattern": "{brand_a}-vs-{brand_b}",
        "title": "{Brand_A} vs {Brand_B}: Welke is Beter in {year}?",
        "prompt_template": """Schrijf een professioneel vergelijkingsartikel: {Brand_A} vs {Brand_B}.

Structuur:
1. Korte intro (2 zinnen)
2. Quick verdict tabel (features, pricing, ease of use, rating)
3. {Brand_A} - Sterke punten (3-4 bullets)
4. {Brand_B} - Sterke punten (3-4 bullets)
5. Head-to-head vergelijking per categorie (features, pricing, support, integrations)
6. Conclusie: wie kiest wat

BELANGRIJK:
- Gebruik affiliate links waar beschikbaar
- Wees eerlijk en objectief
- Focus op waarde voor de lezer
- 1500-2500 woorden
- Dark theme HTML met professionele styling"""
    },
    "alternatives": {
        "pattern": "beste-{brand}-alternatieven",
        "title": "Top 5 {Brand} Alternatieven in {year}",
        "prompt_template": """Schrijf een artikel over de top 5 alternatieven voor {Brand}.

Structuur:
1. Intro: waarom mensen alternatieven zoeken (2 zinnen)
2. Quick comparison tabel
3. Per alternatief: naam, sterke punten, pricing, voor wie
4. Conclusie: welk alternatief past bij welk type gebruiker

BELANGRIJK: Gebruik affiliate links, 1500-2500 woorden, dark theme HTML"""
    },
    "pricing": {
        "pattern": "{brand}-pricing-kosten",
        "title": "{Brand} Pricing & Kosten: Compleet Overzicht {year}",
        "prompt_template": """Schrijf een uitgebreid pricing artikel over {Brand}.

Structuur:
1. Intro: wat kost {Brand}?
2. Pricing tabel (alle plans)
3. Hidden costs / extras
4. Is het de prijs waard? (ROI analyse)
5. Goedkopere alternatieven
6. Conclusie + beste deal tips

BELANGRIJK: Actuele prijzen, affiliate link, 1200-2000 woorden, dark theme HTML"""
    },
    "usecase": {
        "pattern": "beste-ai-tools-voor-{usecase}",
        "title": "Beste AI Tools voor {Usecase} in {year}",
        "prompt_template": """Schrijf een roundup artikel: Beste AI Tools voor {Usecase}.

Structuur:
1. Intro: waarom AI tools voor {usecase}
2. Top 5-7 tools met korte review per tool
3. Vergelijkingstabel (prijs, features, rating)
4. Welke tool voor welk budget/niveau
5. Conclusie

BELANGRIJK: Include onze affiliate brands waar relevant, 1500-2500 woorden, dark theme HTML"""
    }
}

# Use cases voor roundup artikelen
USE_CASES = [
    "video-maken", "presentaties", "website-bouwen", "voice-over",
    "content-creatie", "social-media", "email-marketing", "seo",
    "e-commerce", "freelancers", "startups", "onderwijs",
    "podcast", "muziek-productie", "grafisch-ontwerp", "copywriting"
]


def generate_programmatic_combinations():
    """Genereer alle mogelijke pagina-combinaties uit templates."""
    brands = list(VAULT.keys())
    combinations = []

    # VS combinaties (elke brand vs elke andere)
    for i, a in enumerate(brands):
        for b in brands[i+1:]:
            slug = f"{a.lower()}-vs-{b.lower()}"
            combinations.append({
                "type": "vs",
                "slug": slug,
                "brand_a": a,
                "brand_b": b,
                "title": PROGRAMMATIC_TEMPLATES["vs"]["title"].format(
                    Brand_A=a, Brand_B=b, year=datetime.now().year
                )
            })

    # Alternatives per brand
    for brand in brands:
        slug = f"beste-{brand.lower()}-alternatieven"
        combinations.append({
            "type": "alternatives",
            "slug": slug,
            "brand": brand,
            "title": PROGRAMMATIC_TEMPLATES["alternatives"]["title"].format(
                Brand=brand, year=datetime.now().year
            )
        })

    # Pricing per brand
    for brand in brands:
        slug = f"{brand.lower()}-pricing-kosten"
        combinations.append({
            "type": "pricing",
            "slug": slug,
            "brand": brand,
            "title": PROGRAMMATIC_TEMPLATES["pricing"]["title"].format(
                Brand=brand, year=datetime.now().year
            )
        })

    # Use case roundups
    for uc in USE_CASES:
        slug = f"beste-ai-tools-voor-{uc}"
        uc_display = uc.replace("-", " ").title()
        combinations.append({
            "type": "usecase",
            "slug": slug,
            "usecase": uc,
            "title": PROGRAMMATIC_TEMPLATES["usecase"]["title"].format(
                Usecase=uc_display, year=datetime.now().year
            )
        })

    return combinations


def generate_programmatic_page(combo):
    """Genereer een enkele programmatic SEO pagina."""
    template = PROGRAMMATIC_TEMPLATES.get(combo["type"])
    if not template:
        return None

    # Check of pagina al bestaat
    b2b_path = f"{REPO_ROOT}/b2b"
    target_file = f"{b2b_path}/{combo['slug']}.html"
    if os.path.exists(target_file):
        return None  # Al gemaakt

    # Build prompt
    if combo["type"] == "vs":
        prompt = template["prompt_template"].format(
            Brand_A=combo["brand_a"], Brand_B=combo["brand_b"]
        )
        # Add affiliate links
        links_info = []
        for brand in [combo["brand_a"], combo["brand_b"]]:
            if brand in VAULT:
                links_info.append(f"Affiliate link {brand}: {VAULT[brand]}")
        if links_info:
            prompt += "\n\nAffiliate links:\n" + "\n".join(links_info)

    elif combo["type"] == "alternatives":
        prompt = template["prompt_template"].format(Brand=combo["brand"])
        # Add all affiliate links als alternatieven
        links_info = [f"{b}: {url}" for b, url in VAULT.items() if b != combo["brand"]]
        prompt += "\n\nBeschikbare affiliate links:\n" + "\n".join(links_info)

    elif combo["type"] == "pricing":
        prompt = template["prompt_template"].format(Brand=combo["brand"])
        if combo["brand"] in VAULT:
            prompt += f"\n\nAffiliate link: {VAULT[combo['brand']]}"

    elif combo["type"] == "usecase":
        uc_display = combo["usecase"].replace("-", " ").title()
        prompt = template["prompt_template"].format(Usecase=uc_display)
        links_info = [f"{b}: {url}" for b, url in VAULT.items()]
        prompt += "\n\nBeschikbare affiliate links:\n" + "\n".join(links_info)

    else:
        return None

    # Generate met Claude
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Je bent een SEO content expert. Schrijf complete, professionele HTML artikelen met dark theme styling. Gebruik moderne, schone HTML met inline CSS."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        html_content = res.choices[0].message.content.strip()

        # Extract HTML als het in code blocks zit
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()

        # Schrijf bestand
        os.makedirs(b2b_path, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Track
        prog = load_programmatic()
        prog["generated_pages"].append({
            "slug": combo["slug"],
            "type": combo["type"],
            "title": combo["title"],
            "date": str(datetime.now().date()),
            "file": target_file
        })
        prog["stats"][combo["type"]] = prog["stats"].get(combo["type"], 0) + 1
        save_programmatic(prog)

        return combo["slug"]
    except Exception as e:
        log(f"Programmatic generation error for {combo['slug']}: {e}")
        return None


def programmatic_batch(max_pages=3):
    """Genereer een batch programmatic pagina's (max per keer om API te sparen)."""
    combos = generate_programmatic_combinations()
    b2b_path = f"{REPO_ROOT}/b2b"

    # Filter bestaande
    new_combos = []
    for c in combos:
        if not os.path.exists(f"{b2b_path}/{c['slug']}.html"):
            new_combos.append(c)

    if not new_combos:
        return [], len(combos)

    # Prioriteer op type: vs > alternatives > pricing > usecase
    priority = {"vs": 1, "alternatives": 2, "pricing": 3, "usecase": 4}
    new_combos.sort(key=lambda x: priority.get(x["type"], 5))

    generated = []
    for combo in new_combos[:max_pages]:
        slug = generate_programmatic_page(combo)
        if slug:
            generated.append(slug)
            time.sleep(2)  # Rate limiting

    # Git push als er pagina's zijn gegenereerd
    if generated:
        try:
            rebuild_sitemap()
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: {len(generated)} programmatic SEO pages' && git push origin main")
        except:
            pass

    return generated, len(combos)


# ── 10B: SCHEMA MARKUP ENGINE ─────────────────────────────────────────────

SCHEMA_TEMPLATES = {
    "article": '''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "author": {{"@type": "Organization", "name": "AI Builder Marketplace"}},
  "publisher": {{"@type": "Organization", "name": "AI Builder Marketplace", "url": "https://aibuildermarketplace.com"}},
  "datePublished": "{date}",
  "dateModified": "{modified}",
  "description": "{description}",
  "mainEntityOfPage": "{url}"
}}
</script>''',

    "faq": '''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{faq_items}]
}}
</script>''',

    "product_review": '''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Review",
  "itemReviewed": {{"@type": "SoftwareApplication", "name": "{product}", "applicationCategory": "AI Tool"}},
  "author": {{"@type": "Organization", "name": "AI Builder Marketplace"}},
  "reviewRating": {{"@type": "Rating", "ratingValue": "{rating}", "bestRating": "5"}},
  "reviewBody": "{review_summary}"
}}
</script>''',

    "comparison": '''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{title}",
  "description": "{description}",
  "speakable": {{"@type": "SpeakableSpecification", "cssSelector": ["h1", ".verdict"]}},
  "mainEntity": {{
    "@type": "ItemList",
    "itemListElement": [{items}]
  }}
}}
</script>''',

    "howto": '''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{title}",
  "description": "{description}",
  "step": [{steps}]
}}
</script>'''
}


def detect_article_type(filename, content):
    """Detecteer het type artikel voor juiste schema markup."""
    slug = filename.replace('.html', '').lower()
    content_lower = content.lower()

    if 'vs' in slug or 'versus' in slug:
        return "comparison"
    elif 'alternative' in slug:
        return "comparison"
    elif 'review' in slug or 'review' in content_lower[:500]:
        return "product_review"
    elif 'pricing' in slug or 'kosten' in slug:
        return "product_review"
    elif 'how' in slug or 'tutorial' in slug or 'guide' in slug:
        return "howto"
    else:
        return "article"


def generate_faq_schema(content, slug):
    """Genereer FAQ schema via Claude AI analyse."""
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Genereer 3-5 FAQ vragen en antwoorden gebaseerd op dit artikel. Antwoord ALLEEN in JSON format: [{\"q\": \"vraag\", \"a\": \"antwoord\"}]"},
                {"role": "user", "content": content[:3000]}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        faq_text = res.choices[0].message.content.strip()
        if "```json" in faq_text:
            faq_text = faq_text.split("```json")[1].split("```")[0]
        elif "```" in faq_text:
            faq_text = faq_text.split("```")[1].split("```")[0]
        faqs = json.loads(faq_text)

        items = []
        for faq in faqs:
            items.append(f'{{"@type":"Question","name":"{faq["q"]}","acceptedAnswer":{{"@type":"Answer","text":"{faq["a"]}"}}}}')

        return SCHEMA_TEMPLATES["faq"].format(faq_items=",".join(items))
    except Exception as e:
        log(f"FAQ schema generation error for {slug}: {e}")
        return ""


def add_schema_to_article(filepath):
    """Voeg schema markup toe aan een enkel artikel."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip als er al schema in zit
        if 'application/ld+json' in content:
            return None

        filename = os.path.basename(filepath)
        slug = filename.replace('.html', '')
        article_type = detect_article_type(filename, content)

        schemas = []
        url = f"https://aibuildermarketplace.com/b2b/{slug}.html"
        today = str(datetime.now().date())

        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', content)
        title = title_match.group(1) if title_match else slug.replace('-', ' ').title()

        # Extract description (eerste 160 chars tekst)
        text_only = re.sub(r'<[^>]+>', '', content)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        description = text_only[:160].rsplit(' ', 1)[0] + "..."

        # Basis Article schema altijd toevoegen
        schemas.append(SCHEMA_TEMPLATES["article"].format(
            title=title, date=today, modified=today,
            description=description, url=url
        ))

        # Type-specifiek schema
        if article_type == "product_review":
            brand = None
            for b in VAULT:
                if b.lower() in slug:
                    brand = b
                    break
            if brand:
                schemas.append(SCHEMA_TEMPLATES["product_review"].format(
                    product=brand, rating="4.5",
                    review_summary=description
                ))

        elif article_type == "comparison":
            # Extract vergeleken items
            brands_in_slug = [b for b in VAULT if b.lower() in slug]
            items = []
            for i, brand in enumerate(brands_in_slug, 1):
                items.append(f'{{"@type":"ListItem","position":{i},"name":"{brand}"}}')
            if items:
                schemas.append(SCHEMA_TEMPLATES["comparison"].format(
                    title=title, description=description,
                    items=",".join(items)
                ))

        # FAQ schema via AI (voor alle types)
        faq_schema = generate_faq_schema(content, slug)
        if faq_schema:
            schemas.append(faq_schema)

        # Inject schemas voor </head>
        schema_block = "\n".join(schemas)
        if '</head>' in content:
            content = content.replace('</head>', f'\n{schema_block}\n</head>')
        else:
            content = schema_block + "\n" + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Track
        sd = load_schema_data()
        sd["articles_with_schema"].append({
            "slug": slug,
            "type": article_type,
            "schemas": [s.split('"@type"')[1].split('"')[1] if '"@type"' in s else "unknown" for s in schemas],
            "date": today
        })
        sd["articles_with_schema"] = sd["articles_with_schema"][-200:]
        sd["schema_types"][article_type] = sd["schema_types"].get(article_type, 0) + 1
        save_schema_data(sd)

        return slug
    except Exception as e:
        log(f"Schema injection error for {filepath}: {e}")
        return None


def schema_batch(max_articles=5):
    """Voeg schema markup toe aan artikelen die het nog niet hebben."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return [], 0

    files = [f for f in os.listdir(b2b_path) if f.endswith('.html')]
    processed = []

    for f in files[:max_articles * 3]:  # Check meer, skip bestaande
        if len(processed) >= max_articles:
            break
        filepath = os.path.join(b2b_path, f)
        result = add_schema_to_article(filepath)
        if result:
            processed.append(result)
            time.sleep(1)

    if processed:
        try:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: schema markup for {len(processed)} articles' && git push origin main")
        except:
            pass

    return processed, len(files)


# ── 10C: MULTI-CHANNEL SYNDICATIE ─────────────────────────────────────────

def generate_syndication_variants(slug):
    """Genereer content varianten voor verschillende platformen."""
    b2b_path = f"{REPO_ROOT}/b2b"
    filepath = f"{b2b_path}/{slug}.html"

    if not os.path.exists(filepath):
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract tekst
    text_only = re.sub(r'<[^>]+>', '', content)
    text_only = re.sub(r'\s+', ' ', text_only).strip()

    variants = {}

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": """Je bent een content specialist. Genereer platform-specifieke varianten.
Antwoord in JSON:
{
    "devto": "Markdown artikel (500-800 woorden, technische focus, met frontmatter: title, tags, canonical_url)",
    "medium": "Markdown artikel (600-1000 woorden, storytelling, eerste persoon)",
    "reddit": "Reddit post (200-400 woorden, casual, waarde-gericht, geen promotie-toon)",
    "linkedin": "LinkedIn post (150-250 woorden, professioneel, met emoji bullets)"
}"""},
                {"role": "user", "content": f"Origineel artikel ({slug}):\n\n{text_only[:3000]}\n\nCanonical URL: https://aibuildermarketplace.com/b2b/{slug}.html"}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        result = res.choices[0].message.content.strip()
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        variants = json.loads(result)
    except Exception as e:
        log(f"Syndication variant error for {slug}: {e}")

    return variants


def syndication_cycle(max_articles=2):
    """Genereer syndication content voor recente artikelen."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return []

    synd = load_syndication()
    already_done = {s["slug"] for s in synd.get("syndicated", [])}

    files = sorted(
        [f for f in os.listdir(b2b_path) if f.endswith('.html')],
        key=lambda f: os.path.getmtime(os.path.join(b2b_path, f)),
        reverse=True
    )

    results = []
    syndication_dir = f"{REPO_ROOT}/syndication"
    os.makedirs(syndication_dir, exist_ok=True)

    for f in files:
        if len(results) >= max_articles:
            break
        slug = f.replace('.html', '')
        if slug in already_done:
            continue

        variants = generate_syndication_variants(slug)
        if not variants:
            continue

        # Sla varianten op als bestanden
        saved = []
        for platform, content in variants.items():
            ext = "md" if platform in ["devto", "medium"] else "txt"
            outfile = f"{syndication_dir}/{slug}_{platform}.{ext}"
            with open(outfile, 'w', encoding='utf-8') as fout:
                fout.write(content)
            saved.append(platform)

        synd["syndicated"].append({
            "slug": slug,
            "platforms": saved,
            "date": str(datetime.now().date())
        })

        for p in saved:
            synd["platforms"][p] = synd["platforms"].get(p, 0) + 1

        results.append(f"{slug} → {', '.join(saved)}")
        time.sleep(2)

    save_syndication(synd)

    if results:
        try:
            run_command(f"cd {REPO_ROOT} && git add syndication/ && git commit -m 'Victor: syndication content for {len(results)} articles' && git push origin main")
        except:
            pass

    return results


# ── 10D: SMART INTERNAL LINK GRAPH ───────────────────────────────────────

def scan_internal_links():
    """Scan alle artikelen en bouw een link graph."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return {}

    files = [f for f in os.listdir(b2b_path) if f.endswith('.html')]
    graph = {}  # slug -> {outgoing: [], incoming: [], score: 0}

    # Stap 1: Scan alle links
    for f in files:
        slug = f.replace('.html', '')
        filepath = os.path.join(b2b_path, f)
        try:
            with open(filepath, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except:
            continue

        # Find interne links
        internal_links = re.findall(r'href="(?:\.\/|\/b2b\/)?([^"]+?)\.html"', content)
        # Also check for relative links
        internal_links += re.findall(r'href="([^"]*?)"[^>]*>.*?</a>', content)
        internal_links = [l.replace('.html', '').split('/')[-1] for l in internal_links
                         if 'b2b' in l or (not l.startswith('http') and not l.startswith('#') and not l.startswith('mailto'))]

        graph[slug] = {
            "outgoing": list(set(internal_links)),
            "incoming": [],
            "word_count": len(re.sub(r'<[^>]+>', '', content).split()),
            "has_affiliate": any(url in content for url in VAULT.values()),
            "score": 0
        }

    # Stap 2: Bereken incoming links
    for slug, data in graph.items():
        for target in data["outgoing"]:
            if target in graph:
                graph[target]["incoming"].append(slug)

    # Stap 3: Bereken link scores (simpele PageRank-achtig)
    total_pages = len(graph) or 1
    for slug, data in graph.items():
        incoming_count = len(data["incoming"])
        outgoing_count = len(data["outgoing"])
        has_affiliate = data["has_affiliate"]

        # Score: meer incoming = beter, geld-pagina's moeten meer incoming krijgen
        score = incoming_count * 10
        if has_affiliate:
            score += 20  # Money pages zijn belangrijker
        if outgoing_count == 0:
            score -= 10  # Dead-end pagina's moeten links krijgen
        if incoming_count == 0:
            score -= 15  # Orphan pagina's zijn slecht

        graph[slug]["score"] = max(0, score)

    return graph


def generate_link_recommendations():
    """Genereer aanbevelingen voor interne links."""
    graph = scan_internal_links()
    if not graph:
        return []

    recommendations = []

    # Vind orphan pages (geen incoming links)
    orphans = [slug for slug, data in graph.items() if not data["incoming"]]
    for slug in orphans:
        # Vind gerelateerde pagina's op basis van slug-woorden
        words = slug.split('-')
        related = []
        for other_slug in graph:
            if other_slug != slug:
                other_words = other_slug.split('-')
                overlap = set(words) & set(other_words)
                if overlap - {'vs', 'de', 'het', 'en', 'voor', 'met', 'best', 'beste', 'top'}:
                    related.append(other_slug)

        if related:
            recommendations.append({
                "type": "orphan",
                "target": slug,
                "action": f"Voeg link naar '{slug}' toe vanuit: {', '.join(related[:3])}",
                "priority": "high",
                "from_pages": related[:3]
            })

    # Vind money pages met te weinig incoming links
    for slug, data in graph.items():
        if data["has_affiliate"] and len(data["incoming"]) < 3:
            recommendations.append({
                "type": "money_page",
                "target": slug,
                "action": f"Money page '{slug}' heeft maar {len(data['incoming'])} incoming links, moet 3+",
                "priority": "high",
                "current_incoming": len(data["incoming"])
            })

    # Vind dead-end pages (geen outgoing links)
    dead_ends = [slug for slug, data in graph.items() if not data["outgoing"]]
    for slug in dead_ends:
        recommendations.append({
            "type": "dead_end",
            "target": slug,
            "action": f"Dead-end pagina '{slug}' — voeg 2-3 interne links toe",
            "priority": "medium"
        })

    # Sorteer op prioriteit
    prio_map = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda r: prio_map.get(r["priority"], 2))

    # Save
    lg = load_linkgraph()
    lg["pages"] = {slug: {"in": len(d["incoming"]), "out": len(d["outgoing"]), "score": d["score"]}
                   for slug, d in graph.items()}
    lg["link_scores"] = {slug: d["score"] for slug, d in graph.items()}
    lg["recommendations"] = recommendations
    lg["last_scan"] = str(datetime.now())
    save_linkgraph(lg)

    return recommendations


def auto_fix_internal_links(max_fixes=3):
    """Automatisch interne links toevoegen waar ze missen."""
    recommendations = generate_link_recommendations()
    if not recommendations:
        return []

    b2b_path = f"{REPO_ROOT}/b2b"
    fixed = []

    for rec in recommendations[:max_fixes]:
        if rec["type"] == "orphan" and rec.get("from_pages"):
            # Voeg link toe naar orphan vanuit gerelateerde pagina's
            target_slug = rec["target"]
            for source_slug in rec["from_pages"][:1]:  # Max 1 per fix
                source_file = f"{b2b_path}/{source_slug}.html"
                if not os.path.exists(source_file):
                    continue

                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check of link al bestaat
                    if target_slug in content:
                        continue

                    # Voeg link toe voor </body> of aan eind
                    link_html = f'\n<p style="margin-top:20px;padding:15px;background:#1a1a2e;border-radius:8px;border-left:3px solid #6c63ff;">Lees ook: <a href="./{target_slug}.html" style="color:#6c63ff;">{target_slug.replace("-", " ").title()}</a></p>\n'

                    if '</body>' in content:
                        content = content.replace('</body>', f'{link_html}</body>')
                    else:
                        content += link_html

                    with open(source_file, 'w', encoding='utf-8') as f:
                        f.write(content)

                    fixed.append(f"{source_slug} → {target_slug}")
                except Exception as e:
                    log(f"Link fix error: {e}")

        elif rec["type"] == "dead_end":
            # Voeg relevante links toe aan dead-end pagina's
            target_file = f"{b2b_path}/{rec['target']}.html"
            if not os.path.exists(target_file):
                continue

            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Vind gerelateerde pagina's
                target_words = rec["target"].split('-')
                all_files = [f.replace('.html', '') for f in os.listdir(b2b_path) if f.endswith('.html')]
                related = []
                for slug in all_files:
                    if slug != rec["target"]:
                        overlap = set(target_words) & set(slug.split('-'))
                        if overlap - {'vs', 'de', 'het', 'en', 'voor', 'met', 'best', 'beste'}:
                            related.append(slug)

                if related:
                    links_html = '\n<div style="margin-top:30px;padding:20px;background:#1a1a2e;border-radius:8px;">\n<h3 style="color:#6c63ff;">Gerelateerde artikelen</h3>\n'
                    for r in related[:3]:
                        links_html += f'<p><a href="./{r}.html" style="color:#e0e0ff;">{r.replace("-", " ").title()}</a></p>\n'
                    links_html += '</div>\n'

                    if '</body>' in content:
                        content = content.replace('</body>', f'{links_html}</body>')
                    else:
                        content += links_html

                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(content)

                    fixed.append(f"{rec['target']} ← {len(related[:3])} links added")
            except Exception as e:
                log(f"Dead-end fix error: {e}")

    if fixed:
        try:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: auto-fixed {len(fixed)} internal links' && git push origin main")
        except:
            pass

    return fixed


# ── 10E: REAL-TIME SERP TRACKER ──────────────────────────────────────────

def update_serp_tracking():
    """Update SERP posities vanuit GSC data en detecteer veranderingen."""
    serp = load_serp_data()
    alerts = []

    if not os.path.exists(GSC_DATA_FILE):
        return alerts

    try:
        with open(GSC_DATA_FILE) as f:
            gsc = json.load(f)
    except:
        return alerts

    pages = gsc.get("pages", [])
    queries = gsc.get("queries", [])
    today = str(datetime.now().date())

    # Update tracking per pagina
    tracking = serp.get("tracking", {})
    for page in pages:
        url = page.get("page", "")
        slug = url.split('/')[-1].replace('.html', '') if '/' in url else url
        position = page.get("position", 0)
        clicks = page.get("clicks", 0)
        impressions = page.get("impressions", 0)

        if slug not in tracking:
            tracking[slug] = {
                "positions": [],
                "best_position": position,
                "worst_position": position,
                "trend": "new"
            }

        hist = tracking[slug]
        hist["positions"].append({"date": today, "pos": position, "clicks": clicks, "impr": impressions})
        hist["positions"] = hist["positions"][-30:]  # 30 dagen history

        # Update best/worst
        if position < hist.get("best_position", 100):
            hist["best_position"] = position
        if position > hist.get("worst_position", 0):
            hist["worst_position"] = position

        # Trend detectie
        positions_list = [p["pos"] for p in hist["positions"]]
        if len(positions_list) >= 3:
            recent_avg = sum(positions_list[-3:]) / 3
            older_avg = sum(positions_list[:3]) / 3 if len(positions_list) >= 6 else recent_avg

            if recent_avg < older_avg - 5:
                hist["trend"] = "rising"
            elif recent_avg > older_avg + 5:
                hist["trend"] = "falling"
            else:
                hist["trend"] = "stable"

        # Alerts
        if len(positions_list) >= 2:
            change = positions_list[-1] - positions_list[-2]
            if change <= -5:
                alert = f"📈 {slug}: +{abs(change)} posities omhoog! (nu #{positions_list[-1]:.0f})"
                alerts.append(alert)
            elif change >= 5:
                alert = f"📉 {slug}: -{change} posities omlaag! (nu #{positions_list[-1]:.0f})"
                alerts.append(alert)

            # Page 1 entry alert
            if positions_list[-1] <= 10 and positions_list[-2] > 10:
                alert = f"🏆 {slug}: PAGINA 1 bereikt! (positie #{positions_list[-1]:.0f})"
                alerts.append(alert)
                # Trigger chain reaction
                try:
                    trigger_chain_reaction(slug, "page1")
                except:
                    pass

            # Page 1 verloren alert
            if positions_list[-1] > 10 and positions_list[-2] <= 10:
                alert = f"⚠️ {slug}: Pagina 1 VERLOREN (nu #{positions_list[-1]:.0f})"
                alerts.append(alert)

    serp["tracking"] = tracking
    serp["alerts"].extend([{"alert": a, "date": today} for a in alerts])

    # Dagelijkse snapshot
    total_pages = len(tracking)
    page1_count = sum(1 for s, d in tracking.items()
                      if d["positions"] and d["positions"][-1]["pos"] <= 10)
    top3_count = sum(1 for s, d in tracking.items()
                     if d["positions"] and d["positions"][-1]["pos"] <= 3)
    rising = sum(1 for s, d in tracking.items() if d.get("trend") == "rising")
    falling = sum(1 for s, d in tracking.items() if d.get("trend") == "falling")

    serp["daily_snapshots"].append({
        "date": today,
        "total": total_pages,
        "page1": page1_count,
        "top3": top3_count,
        "rising": rising,
        "falling": falling
    })

    save_serp_data(serp)
    return alerts


def generate_serp_report():
    """Genereer een volledig SERP tracking rapport."""
    serp = load_serp_data()
    tracking = serp.get("tracking", {})

    msg = "📊 SERP Tracker — Positie Rapport\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if not tracking:
        msg += "Nog geen tracking data. Run /gsc fetch eerst.\n"
        return msg

    # Summary
    total = len(tracking)
    page1 = sum(1 for s, d in tracking.items()
                if d["positions"] and d["positions"][-1]["pos"] <= 10)
    top3 = sum(1 for s, d in tracking.items()
               if d["positions"] and d["positions"][-1]["pos"] <= 3)

    msg += f"📈 Totaal getrackt: {total} pagina's\n"
    msg += f"🥇 Pagina 1: {page1} ({page1/total*100:.0f}%)\n"
    msg += f"🏆 Top 3: {top3}\n\n"

    # Rising stars
    rising = [(s, d) for s, d in tracking.items() if d.get("trend") == "rising"]
    if rising:
        msg += "🚀 Stijgers:\n"
        for slug, data in sorted(rising, key=lambda x: x[1]["positions"][-1]["pos"])[:5]:
            pos = data["positions"][-1]["pos"]
            msg += f"  ↑ {slug[:35]}: #{pos:.0f}\n"

    # Falling
    falling = [(s, d) for s, d in tracking.items() if d.get("trend") == "falling"]
    if falling:
        msg += "\n📉 Dalers:\n"
        for slug, data in sorted(falling, key=lambda x: x[1]["positions"][-1]["pos"])[:5]:
            pos = data["positions"][-1]["pos"]
            msg += f"  ↓ {slug[:35]}: #{pos:.0f}\n"

    # Recent alerts
    alerts = serp.get("alerts", [])[-5:]
    if alerts:
        msg += "\n🔔 Recente Alerts:\n"
        for a in alerts:
            msg += f"  {a['alert']}\n"

    # Trend over time
    snapshots = serp.get("daily_snapshots", [])
    if len(snapshots) >= 2:
        first = snapshots[0]
        last = snapshots[-1]
        msg += f"\n📊 Trend ({first['date']} → {last['date']}):\n"
        msg += f"  Pagina 1: {first.get('page1', 0)} → {last.get('page1', 0)}\n"
        msg += f"  Top 3: {first.get('top3', 0)} → {last.get('top3', 0)}\n"

    return msg


def domination_matrix_cycle():
    """Volledige Domination Matrix cyclus — draait dagelijks."""
    actions = []

    # 1. SERP tracking update
    try:
        alerts = update_serp_tracking()
        if alerts:
            actions.extend(alerts)
        actions.append(f"📊 SERP tracking bijgewerkt")
    except Exception as e:
        log(f"SERP tracking error: {e}")

    # 2. Schema markup batch (max 2 per dag)
    try:
        schema_done, total = schema_batch(max_articles=2)
        if schema_done:
            actions.append(f"🏷️ Schema markup toegevoegd aan {len(schema_done)} artikelen")
    except Exception as e:
        log(f"Schema batch error: {e}")

    # 3. Internal link fixes (max 2 per dag)
    try:
        link_fixes = auto_fix_internal_links(max_fixes=2)
        if link_fixes:
            actions.append(f"🔗 {len(link_fixes)} interne links gefixed")
    except Exception as e:
        log(f"Link fix error: {e}")

    # 4. Programmatic SEO (max 1 per dag — API sparen)
    try:
        prog_done, total_possible = programmatic_batch(max_pages=1)
        if prog_done:
            actions.append(f"🏭 {len(prog_done)} programmatic pagina's gegenereerd ({total_possible} totaal mogelijk)")
    except Exception as e:
        log(f"Programmatic batch error: {e}")

    # 5. Syndication (1x per week, alleen op dinsdag)
    if datetime.now().weekday() == 1:  # Dinsdag
        try:
            synd_results = syndication_cycle(max_articles=1)
            if synd_results:
                actions.append(f"📢 Syndication content voor {len(synd_results)} artikelen")
        except Exception as e:
            log(f"Syndication error: {e}")

    return actions


# ── TELEGRAM BOT ─────────────────────────────────────────────────────────────
bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['status'])
def cmd_status(message):
    if message.from_user.id != ADMIN_ID:
        return
    report = generate_status_report()
    bot.reply_to(message, report)

@bot.message_handler(commands=['logs'])
def cmd_logs(message):
    if message.from_user.id != ADMIN_ID:
        return
    out = run_command("tail -20 /root/felix_hq/cron.log")
    bot.reply_to(message, f"📋 Laatste cron output:\n{out}")

@bot.message_handler(commands=['articles'])
def cmd_articles(message):
    if message.from_user.id != ADMIN_ID:
        return
    out = run_command(f"ls -t {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | head -15")
    count = run_command(f"ls {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | wc -l")
    bot.reply_to(message, f"📊 {count.strip()} artikelen\n\nLaatste 15:\n{out}")

@bot.message_handler(commands=['generate'])
def cmd_generate(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "⏳ Artikel genereren met Claude...")
    out = run_command("cd /root/felix_hq && OPENROUTER_KEY=$OPENROUTER_KEY /root/felix_hq/venv/bin/python3 generate_article.py", timeout=180)
    bot.reply_to(message, f"📋 {out}")

@bot.message_handler(commands=['seo'])
def cmd_seo(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔍 SEO check bezig...")
    # Check sitemap, robots, article count, missing meta tags
    checks = []
    sitemap = run_command(f"wc -l < {REPO_ROOT}/sitemap.xml")
    checks.append(f"Sitemap: {sitemap.strip()} regels")
    robots = run_command(f"cat {REPO_ROOT}/robots.txt 2>/dev/null | head -5")
    checks.append(f"Robots.txt: {'OK' if 'Sitemap' in robots else '⚠️ Geen sitemap referentie'}")
    total = run_command(f"ls {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | wc -l")
    checks.append(f"Artikelen: {total.strip()}")
    # Check hoeveel artikelen og:image missen
    missing_og = run_command(f"grep -rL 'og:image' {REPO_ROOT}/b2b/*/index.html 2>/dev/null | wc -l")
    checks.append(f"Zonder og:image: {missing_og.strip()}")
    # Check hoeveel artikelen affiliate links missen
    missing_aff = run_command(f"grep -rL 'nofollow sponsored' {REPO_ROOT}/b2b/*/index.html 2>/dev/null | wc -l")
    checks.append(f"Zonder affiliate links: {missing_aff.strip()}")
    # Per tool
    for brand in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
        count = run_command(f"ls {REPO_ROOT}/b2b/ | grep '^{brand}' | wc -l")
        checks.append(f"  {brand}: {count.strip()} artikelen")
    bot.reply_to(message, "📊 SEO Rapport:\n" + "\n".join(checks))

@bot.message_handler(commands=['affcheck'])
def cmd_affcheck(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "💰 Affiliate link check...")
    checks = []
    # Check of alle affiliate links correct zijn
    for brand, url in VAULT.items():
        if brand == "Clay":
            continue
        count = run_command(f"grep -rl '{url}' {REPO_ROOT}/b2b/*/index.html 2>/dev/null | wc -l")
        checks.append(f"{brand}: {count.strip()} artikelen met werkende affiliate link")
    # Check of CTA's aanwezig zijn
    cta_count = run_command(f"grep -rl 'Get Started with' {REPO_ROOT}/b2b/*/index.html 2>/dev/null | wc -l")
    checks.append(f"\nCTA buttons: {cta_count.strip()} artikelen")
    # Schat potentieel
    total = run_command(f"ls {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | wc -l")
    checks.append(f"Totaal artikelen: {total.strip()}")
    checks.append(f"\n💡 Tip: focus op Kinsta (hoogste commissie) en Synthesia (trending)")
    bot.reply_to(message, "💰 Revenue Rapport:\n" + "\n".join(checks))

@bot.message_handler(commands=['strategy'])
def cmd_strategy(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    # Verzamel data voor strategisch advies
    data = {}
    data['total'] = run_command(f"ls {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | wc -l").strip()
    for brand in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
        data[brand] = run_command(f"ls {REPO_ROOT}/b2b/ | grep '^{brand}' | wc -l").strip()
    data['latest'] = run_command(f"ls -t {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | head -3")
    data['cron'] = run_command("tail -5 /root/felix_hq/cron.log 2>/dev/null")
    data['disk'] = run_command("df -h / | tail -1 | awk '{print $5}'").strip()

    strategy_prompt = f"""Geef een kort strategisch advies (max 200 woorden) voor AIBuilder Marketplace op basis van deze data:
- Totaal artikelen: {data['total']}
- Per tool: Kinsta {data['kinsta']}, Synthesia {data['synthesia']}, InVideo {data['invideo']}, Replit {data['replit']}, Bitvavo {data['bitvavo']}, Murf {data['murf']}
- Laatste artikelen: {data['latest']}
- Disk usage: {data['disk']}

Focus op: welke tool heeft meer content nodig? Wat is de snelste weg naar meer affiliate revenue? Welke quick wins zijn er?"""

    advice = ask_victor(strategy_prompt, [])
    bot.reply_to(message, f"🧠 Strategisch Advies:\n\n{advice}")

@bot.message_handler(commands=['write'])
def cmd_write(message):
    """Laat Victor een script of file schrijven."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /write <beschrijving van wat je wilt>\nBijv: /write een Python script dat alle broken links checkt")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    task = parts[1]
    history = load_memory()
    reply = ask_victor(f"Daniel wil dat je code schrijft. Taak: {task}\n\nSchrijf de volledige code. Gebruik COMMANDO: om het bestand aan te maken met cat/tee. Leg kort uit wat de code doet.", history)

    # Handle commando's als die er zijn
    if "COMMANDO:" in reply:
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)
        commands = [p.split("\n")[0].strip().strip('`')
                    for p in reply.split("COMMANDO:")[1:]
                    if p.split("\n")[0].strip()][:2]
        for cmd in commands:
            bot.reply_to(message, f"🛠 `{cmd}`")
            out = run_command(cmd, timeout=90)
            bot.reply_to(message, f"📋 {out}")
    else:
        bot.reply_to(message, reply)
    history.append({"role": "assistant", "content": reply})
    save_memory(history)


@bot.message_handler(commands=['multifile'])
def cmd_multifile(message):
    """Complex multi-file refactor: Victor past meerdere bestanden tegelijk aan."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /multifile <beschrijving van de refactor>\n\nBijv:\n/multifile voeg structured data toe aan alle artikelen\n/multifile maak een nieuwe pagina met nav + footer die matcht met index.html\n/multifile refactor generate_article.py: split in modules")
        return

    task = parts[1]
    bot.reply_to(message, f"🏗️ Multi-file taak gestart: {task}\n\nIk maak eerst een plan, dan voer ik alles stap voor stap uit.")
    bot.send_chat_action(message.chat.id, 'typing')

    history = load_memory()

    # Stap 1: Laat Victor een plan maken
    plan_prompt = f"""COMPLEXE MULTI-FILE TAAK: {task}

Maak een gedetailleerd plan:
1. Welke bestanden moeten worden aangepast? (lijst met paden)
2. Wat moet er in elk bestand veranderen?
3. In welke volgorde?
4. Hoe test je of het werkt?

Gebruik COMMANDO: om eerst de relevante bestanden te bekijken (ls, cat, head).
Max 2 COMMANDO: regels om informatie te verzamelen."""

    reply = ask_victor(plan_prompt, history)
    history.append({"role": "assistant", "content": reply})

    # Voer het plan uit via de auto-continue loop
    if "COMMANDO:" in reply:
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        commands = [p.split("\n")[0].strip().strip('`')
                    for p in reply.split("COMMANDO:")[1:]
                    if p.split("\n")[0].strip()][:2]
        all_output = []
        for cmd in commands:
            bot.reply_to(message, f"🛠 `{cmd}`")
            out = run_command(cmd)
            bot.reply_to(message, f"📋 {out}")
            all_output.append(f"$ {cmd}\n{out}")
            time.sleep(0.5)

        combined = "\n".join(all_output)[:2000]
        history.append({"role": "user", "content": f"[Verkenning output]:\n{combined}"})

        # Auto-continue: laat Victor het plan uitvoeren
        MAX_ROUNDS = 20
        for round_num in range(2, MAX_ROUNDS + 1):
            bot.send_chat_action(message.chat.id, 'typing')

            continue_prompt = f"""Output van stap {round_num - 1}:
{combined}

Ga verder met het multi-file plan. Voer de volgende stap uit.
Als je klaar bent met ALLE bestanden: geef een samenvatting en commit alles.
Gebruik max 2 COMMANDO: regels per stap."""

            reply = ask_victor(continue_prompt, history)
            history.append({"role": "assistant", "content": reply})
            log(f"MULTIFILE [stap {round_num}]: {reply[:300]}")

            if "COMMANDO:" not in reply:
                bot.reply_to(message, reply)
                break

            pre_text = reply.split("COMMANDO:")[0].strip()
            if pre_text:
                bot.reply_to(message, pre_text)

            commands = [p.split("\n")[0].strip().strip('`')
                        for p in reply.split("COMMANDO:")[1:]
                        if p.split("\n")[0].strip()][:2]
            all_output = []
            for cmd in commands:
                bot.reply_to(message, f"🛠 [{round_num}] `{cmd}`")
                out = run_command(cmd, timeout=90)
                bot.reply_to(message, f"📋 {out}")
                all_output.append(f"$ {cmd}\n{out}")
                time.sleep(0.5)

            combined = "\n".join(all_output)[:2000]
            history.append({"role": "user", "content": f"[Stap {round_num} output]:\n{combined}"})
        else:
            bot.reply_to(message, f"⚠️ {MAX_ROUNDS} stappen uitgevoerd. Stuur een bericht als ik verder moet.")
    else:
        bot.reply_to(message, reply)

    save_memory(history)

@bot.message_handler(commands=['fix'])
def cmd_fix(message):
    """Persistent problem-solving: Victor stopt niet tot het opgelost is."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /fix <beschrijving van het probleem>\nBijv: /fix artikelen worden niet gepusht naar github")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    problem = parts[1]
    bot.reply_to(message, f"🔧 Ik ga dit oplossen: {problem}\nIk stop pas als het gefixt is.")

    history = load_memory()
    attempt = 0
    max_attempts = 5

    while attempt < max_attempts:
        attempt += 1
        prompt = f"{'Probleem: ' + problem if attempt == 1 else 'De vorige fix werkte niet. Probeer een ANDERE aanpak.'}\n\nPoging {attempt}/{max_attempts}. Diagnose eerst, dan fix. Gebruik max 2 COMMANDO: regels."
        reply = ask_victor(prompt, history)
        history.append({"role": "assistant", "content": reply})

        if "COMMANDO:" not in reply:
            bot.reply_to(message, reply)
            break

        # Voer commando's uit
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        commands = [p.split("\n")[0].strip().strip('`') for p in reply.split("COMMANDO:")[1:] if p.split("\n")[0].strip()][:2]
        outputs = []
        for cmd in commands:
            bot.reply_to(message, f"🛠 [{attempt}/{max_attempts}] `{cmd}`")
            out = run_command(cmd)
            bot.reply_to(message, f"📋 {out}")
            outputs.append(f"$ {cmd}\n{out}")
            time.sleep(0.5)

        combined = "\n".join(outputs)[:1500]
        history.append({"role": "user", "content": f"[Output poging {attempt}]:\n{combined}"})

        # Check of het gelukt is
        verify = ask_victor(f"Output van poging {attempt}:\n{combined}\n\nIs het probleem opgelost? Antwoord met OPGELOST als het werkt, of leg uit wat er nog mis is.", history)
        history.append({"role": "assistant", "content": verify})

        if "OPGELOST" in verify.upper():
            bot.reply_to(message, f"✅ {verify}")
            break
        elif attempt < max_attempts:
            bot.reply_to(message, f"🔄 Poging {attempt} niet gelukt. Volgende aanpak...")
        else:
            bot.reply_to(message, f"⚠️ Na {max_attempts} pogingen niet opgelost.\n\n{verify}\n\nDit heeft handmatige aandacht nodig.")

    save_memory(history)

@bot.message_handler(commands=['uptime'])
def cmd_uptime(message):
    if message.from_user.id != ADMIN_ID:
        return
    results = check_uptime()
    lines = []
    for name, status, detail in results:
        icon = "✅" if status == "OK" else "⚠️" if status == "WARN" else "🔴"
        lines.append(f"{icon} {name}: {detail}")
    bot.reply_to(message, "🌐 Uptime Check:\n" + "\n".join(lines))

@bot.message_handler(commands=['linkcheck'])
def cmd_linkcheck(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔗 Affiliate links checken...")
    results = check_affiliate_links()
    bot.reply_to(message, "🔗 Affiliate Link Health:\n" + "\n".join(results))

@bot.message_handler(commands=['quality'])
def cmd_quality(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "📝 Artikelkwaliteit analyseren...")
    issues = check_article_quality()
    worst = find_worst_articles(5)
    worst_text = "\n".join([f"  {name}: {size//1024}KB" for name, size in worst])
    if issues:
        bot.reply_to(message, f"📝 Kwaliteitsrapport:\n\n{chr(10).join(issues)}\n\n📉 Kleinste artikelen:\n{worst_text}")
    else:
        bot.reply_to(message, f"✅ Alle artikelen zien er goed uit!\n\n📉 Kleinste artikelen:\n{worst_text}")

@bot.message_handler(commands=['optimize'])
def cmd_optimize(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔧 Interne links optimaliseren...")
    fixed = optimize_internal_links()
    if fixed > 0:
        # Commit en push
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: add internal links to {fixed} articles' && git pull --rebase origin main && git push origin main")
        bot.reply_to(message, f"✅ Interne links toegevoegd aan {fixed} artikelen en gepusht!")
    else:
        bot.reply_to(message, "✅ Alle artikelen hebben al interne links.")

@bot.message_handler(commands=['improve'])
def cmd_improve(message):
    """Verbeter het slechtste artikel met Claude."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔍 Slechtste artikel zoeken en verbeteren...")
    worst = find_worst_articles(1)
    if not worst:
        bot.reply_to(message, "Geen artikelen gevonden.")
        return

    folder, size = worst[0]
    article_path = f"{REPO_ROOT}/b2b/{folder}/index.html"
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            old_html = f.read()
    except:
        bot.reply_to(message, f"Kan {folder} niet lezen.")
        return

    # Detecteer brand
    brand = folder.split('-')[0].capitalize()
    if brand == "Invideo":
        brand = "InVideo"

    bot.reply_to(message, f"📝 Verbeteren: {folder} ({size//1024}KB)\nSchrijven met Claude...")
    bot.send_chat_action(message.chat.id, 'typing')

    improve_prompt = f"""Dit artikel over {brand} is te kort/slecht ({size} bytes). Herschrijf het VOLLEDIG als een uitgebreid, SEO-geoptimaliseerd artikel.

Originele slug: {folder}
Brand: {brand}

Schrijf minimaal 2000 woorden. Gebruik HTML tags (geen <html>, <head>, <body>). Structuur:
1. Pakkende H1 headline
2. Intro met het probleem dat {brand} oplost
3. Gedetailleerde feature review met concrete voorbeelden
4. Pricing overzicht met tiers
5. Echte use case met cijfers
6. Pros & Cons
7. FAQ (4-5 vragen)
8. Conclusie met duidelijke aanbeveling

Schrijf als een ervaren founder, niet als een AI. Gebruik specifieke cijfers en voorbeelden."""

    try:
        res = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": improve_prompt}], max_tokens=4000
        )
        new_content = res.choices[0].message.content.replace("```html", "").replace("```", "")

        # Bouw nieuwe pagina met de bestaande template-structuur
        # Behoud meta tags en scripts van het origineel als die er zijn
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(old_html.split('</head>')[0] + '</head><body style="background:#0d1117;color:#e6edf3;font-family:system-ui;max-width:800px;margin:0 auto;padding:20px;">' + new_content + '</body></html>' if '</head>' in old_html else new_content)

        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: improved {folder}' && git pull --rebase origin main && git push origin main")
        new_size = os.path.getsize(article_path)
        bot.reply_to(message, f"✅ {folder} verbeterd!\n{size//1024}KB → {new_size//1024}KB")
    except Exception as e:
        bot.reply_to(message, f"❌ Fout bij verbeteren: {e}")

@bot.message_handler(commands=['redesign'])
def cmd_redesign(message):
    """Redesign een pagina van de website met professioneel design."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /redesign <pagina>\n\nVoorbeelden:\n/redesign homepage\n/redesign b2b\n/redesign terms\n/redesign nieuw: /over-ons pagina")
        return

    target = parts[1].strip().lower()
    bot.reply_to(message, f"🎨 Redesigning: {target}\nIk bouw een professionele pagina met modern design...")
    bot.send_chat_action(message.chat.id, 'typing')

    # Bepaal welk bestand
    if target in ['homepage', 'home', 'index', 'landingpage', 'landing']:
        file_path = f"{REPO_ROOT}/index.html"
        page_desc = "de homepage/landing page van AIBuilder Marketplace"
    elif target in ['b2b', 'reviews', 'artikelen']:
        file_path = f"{REPO_ROOT}/b2b/index.html"
        page_desc = "de B2B reviews overzichtspagina"
    elif target.startswith('nieuw:') or target.startswith('new:'):
        page_name = target.split(':', 1)[1].strip()
        slug = re.sub(r'[^a-z0-9-]', '', page_name.replace(' ', '-'))
        os.makedirs(f"{REPO_ROOT}/{slug}", exist_ok=True)
        file_path = f"{REPO_ROOT}/{slug}/index.html"
        page_desc = f"een nieuwe pagina: {page_name}"
    else:
        file_path = f"{REPO_ROOT}/{target}/index.html"
        page_desc = f"de {target} pagina"

    # Lees huidige versie als die bestaat
    old_html = ""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                old_html = f.read()[:2000]
        except:
            pass

    design_prompt = f"""Ontwerp een COMPLETE, professionele HTML pagina voor {page_desc} van AIBuilder Marketplace.

Website: aibuildermarketplace.com (GitHub Pages, static HTML)
Doel: AI tool reviews en affiliate marketing voor 6 tools (Kinsta, Synthesia, InVideo, Replit, Bitvavo, Murf)

DESIGN REQUIREMENTS:
- Dark theme: background #0a0e17, cards #1a1f2e, borders #1e293b
- Accent kleuren: blue #3b82f6, purple #a78bfa, green #10b981, pink #ec4899
- Font: Inter via Google Fonts
- CSS variables voor alle kleuren
- Fully responsive (mobile + tablet + desktop)
- Scroll animations met IntersectionObserver
- Sticky/glass navigation bar
- Gradient accents en hover effecten
- Structured data (JSON-LD)
- Open Graph meta tags
- Affiliate links: rel="nofollow sponsored"

AFFILIATES:
- Kinsta: https://kinsta.com/?kaid=EKSCJEFWBYJO
- Synthesia: https://www.synthesia.io/?via=daniel-haket
- InVideo: https://invideo.sjv.io/E00nbn
- Replit: https://replit.com/signup?referral=dglhaket
- Bitvavo: https://account.bitvavo.com/create?a=68DCE39715
- Murf: https://get.murf.ai/qbhzdrcv3l7x

{'Huidige versie (ter referentie):' + chr(10) + old_html[:1000] if old_html else 'Nieuwe pagina — begin from scratch.'}

Lever ALLEEN de complete HTML op. Geen uitleg, geen markdown code blocks. Start met <!DOCTYPE html> en eindig met </html>.
De pagina moet er professioneel uitzien, als een echte SaaS website, niet als een hobby project."""

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": design_prompt}],
            max_tokens=8000
        )
        new_html = res.choices[0].message.content.strip()
        # Clean up als er markdown code blocks omheen zitten
        if new_html.startswith("```"):
            new_html = new_html.split("\n", 1)[1] if "\n" in new_html else new_html
        if new_html.endswith("```"):
            new_html = new_html.rsplit("```", 1)[0]
        new_html = new_html.strip()
        if not new_html.startswith("<!DOCTYPE") and not new_html.startswith("<html"):
            # Probeer de HTML te extracten
            start = new_html.find("<!DOCTYPE")
            if start == -1:
                start = new_html.find("<html")
            if start >= 0:
                new_html = new_html[start:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_html)

        # Git commit en push
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: redesign {target}' && git pull --rebase origin main && git push origin main")
        bot.reply_to(message, f"✅ {target} is herontworpen en live!\n🌐 Check: https://aibuildermarketplace.com/{'' if 'index' in file_path.split('/')[-2] or file_path == f'{REPO_ROOT}/index.html' else target + '/'}")
    except Exception as e:
        bot.reply_to(message, f"❌ Fout bij redesign: {e}")

@bot.message_handler(commands=['research'])
def cmd_research(message):
    """Trigger web research scan: competitors, affiliate links, SEO trends."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔬 Web research scan gestart...\nIk check de site, competitors, en affiliate links.")
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        findings = web_research_scan()
        research = load_research()
        report = "🔬 Web Research Resultaten\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

        if findings:
            report += "📊 Site Check:\n" + "\n".join(f"  - {f}" for f in findings) + "\n\n"

        if research.get("seo_insights"):
            recent = research["seo_insights"][-6:]
            report += "🔗 Affiliate Link Status:\n" + "\n".join(f"  - {i['insight']}" for i in recent) + "\n\n"

        if research.get("competitors"):
            recent = research["competitors"][-3:]
            report += "🏆 Competitor Intel:\n" + "\n".join(f"  - {c['finding']}" for c in recent) + "\n\n"

        report += f"⏰ Laatste scan: {research.get('last_scan', 'nooit')}"
        bot.reply_to(message, report)
    except Exception as e:
        bot.reply_to(message, f"❌ Research scan error: {e}")


@bot.message_handler(commands=['diagnose'])
def cmd_diagnose(message):
    """Victor analyseert zijn eigen prestaties."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    report = self_diagnose()

    # Voeg aanbevelingen toe via Claude
    try:
        advice_prompt = f"""Op basis van deze self-diagnose, geef 3 concrete verbeteracties (max 100 woorden):

{report}"""
        advice = ask_victor(advice_prompt, [])
        report += f"\n\n💡 Aanbevelingen:\n{advice}"
    except:
        pass

    bot.reply_to(message, report)


@bot.message_handler(commands=['brain'])
def cmd_brain(message):
    """Toon Victor's geleerde kennis: skills, patronen, vermijdingen."""
    if message.from_user.id != ADMIN_ID:
        return

    skills = load_skills()
    long_mem = load_long_memory()
    research = load_research()

    report = "🧠 Victor's Brain — Geleerde Kennis\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Oplossingen
    solutions = skills.get("solutions", {})
    report += f"📚 Opgeslagen oplossingen: {len(solutions)}\n"
    for key, val in list(solutions.items())[-5:]:
        report += f"  - {key[:40]}: {val.get('description', '')[:60]}\n"

    # Vermijdpatronen
    avoided = skills.get("avoided", [])
    report += f"\n🚫 Vermijdpatronen: {len(avoided)}\n"
    for a in avoided[-5:]:
        report += f"  - {a.get('lesson', '')[:80]}\n"

    # Code patronen
    patterns = skills.get("code_patterns", [])
    report += f"\n💻 Geleerde code patronen: {len(patterns)}\n"
    for p in patterns[-5:]:
        report += f"  - {p.get('pattern', '')[:60]}\n"

    # Geheugen stats
    report += f"\n📊 Geheugen:\n"
    report += f"  Facts: {len(long_mem.get('facts', []))}\n"
    report += f"  Wins: {len(long_mem.get('wins', []))}\n"
    report += f"  Errors: {len(long_mem.get('errors', []))}\n"
    report += f"  Research scans: {'ja' if research.get('last_scan') else 'nee'}\n"

    bot.reply_to(message, report)


@bot.message_handler(commands=['autofix'])
def cmd_autofix(message):
    """Auto-improve de slechtste artikelen zonder tussenkomst."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔄 Auto-improve gestart... Ik zoek de slechtste artikelen en herschrijf ze.")
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        improved = auto_improve_articles()
        if improved:
            bot.reply_to(message, f"✅ {len(improved)} artikelen verbeterd:\n" + "\n".join(f"  - {i}" for i in improved))
        else:
            bot.reply_to(message, "✅ Alle artikelen zijn al van goede kwaliteit (>5KB). Geen verbetering nodig.")
    except Exception as e:
        bot.reply_to(message, f"❌ Auto-improve error: {e}")


@bot.message_handler(commands=['revenue'])
def cmd_revenue_intel(message):
    """Revenue intelligence: geschatte earnings, ROI scores, trends."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "💰 Revenue intelligence berekenen...")
    bot.send_chat_action(message.chat.id, 'typing')
    report = generate_revenue_report()
    if len(report) > 4000:
        bot.reply_to(message, report[:4000])
        bot.reply_to(message, report[4000:])
    else:
        bot.reply_to(message, report)


@bot.message_handler(commands=['roi'])
def cmd_roi(message):
    """Toon hoogste ROI acties: wat levert het meeste op per uur?"""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🎯 ROI scores berekenen...")
    bot.send_chat_action(message.chat.id, 'typing')

    roi = calculate_roi_scores()
    if not roi:
        bot.reply_to(message, "Nog geen data. Gebruik eerst /gsc fetch.")
        return

    report = "🎯 ROI Prioritering — Hoogste Waarde Eerst\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, (key, data) in enumerate(list(roi.items())[:10], 1):
        report += f"{i}. €{data.get('roi_per_hour', 0):.0f}/uur — {data['action'][:50]}\n"

    report += "\n💡 Focus op de bovenste acties voor maximale revenue impact."
    bot.reply_to(message, report)


@bot.message_handler(commands=['funnels'])
def cmd_funnels(message):
    """Bouw en toon conversion funnels."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    subcmd = parts[1].strip().lower() if len(parts) > 1 else "show"

    if subcmd == "build":
        bot.reply_to(message, "🔄 Conversion funnels bouwen + links toevoegen...")
        bot.send_chat_action(message.chat.id, 'typing')
        funnels = build_conversion_funnels()
        fixed = apply_funnel_links()
        if fixed > 0:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: funnel links ({fixed} articles)' && git push origin main")
        report = "🔄 Funnels Gebouwd!\n\n"
        for brand, info in funnels.get("funnels", {}).items():
            stages = info.get('stages', {})
            report += f"📦 {brand.capitalize()}: {len(stages.get('awareness', []))} awareness → {len(stages.get('consideration', []))} consideration → {len(stages.get('decision', []))} decision\n"
            if info.get('gaps'):
                for gap in info['gaps']:
                    report += f"   ⚠️ {gap}\n"
        report += f"\n🔗 Funnel links toegevoegd aan {fixed} artikelen"
        bot.reply_to(message, report)
        return

    funnels = build_conversion_funnels()
    report = "🔄 Conversion Funnels\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for brand, info in funnels.get("funnels", {}).items():
        stages = info.get('stages', {})
        report += f"📦 {brand.capitalize()} ({info.get('total', 0)} artikelen):\n"
        report += f"   👁️ Awareness: {len(stages.get('awareness', []))}\n"
        report += f"   🤔 Consideration: {len(stages.get('consideration', []))}\n"
        report += f"   ✅ Decision: {len(stages.get('decision', []))}\n"
    report += "\nGebruik /funnels build om funnel links toe te voegen."
    bot.reply_to(message, report)


@bot.message_handler(commands=['dashboard'])
def cmd_dashboard(message):
    """Genereer en deploy het live admin dashboard."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "📊 Dashboard genereren...")
    bot.send_chat_action(message.chat.id, 'typing')

    # Zorg dat revenue data actueel is
    calculate_article_revenue()

    html = generate_admin_dashboard()
    dashboard_dir = f"{REPO_ROOT}/admin"
    os.makedirs(dashboard_dir, exist_ok=True)
    with open(f"{dashboard_dir}/index.html", 'w', encoding='utf-8') as f:
        f.write(html)

    run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: dashboard update' && git push origin main")
    bot.reply_to(message, "📊 Dashboard LIVE!\n\n🌐 https://aibuildermarketplace.com/admin/\n\n(noindex/nofollow — alleen voor jou)")


@bot.message_handler(commands=['social'])
def cmd_social(message):
    """Genereer social media content voor een artikel."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        # Gebruik het best presterende artikel
        revenue = load_revenue_data()
        top = revenue.get("top_earners", [])
        if top:
            slug = top[0]['slug']
        else:
            bot.reply_to(message, "Gebruik: /social <artikel-slug>\nBijv: /social kinsta-review")
            return
    else:
        slug = parts[1].strip()

    bot.reply_to(message, f"📱 Social content genereren voor {slug}...")
    bot.send_chat_action(message.chat.id, 'typing')
    content = generate_social_content(slug)
    if content:
        bot.reply_to(message, content)
    else:
        bot.reply_to(message, f"❌ Artikel '{slug}' niet gevonden.")


@bot.message_handler(commands=['spy'])
def cmd_spy(message):
    """Competitor intelligence: crawl, analyseer, en domineer."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    subcmd = parts[1].strip().lower() if len(parts) > 1 else "report"

    if subcmd == "scan" or subcmd == "crawl":
        bot.reply_to(message, "🕵️ Competitor sites crawlen...")
        bot.send_chat_action(message.chat.id, 'typing')
        new_content = full_competitor_scan()
        if new_content:
            report = f"🕵️ Scan Resultaten: {len(new_content)} nieuwe artikelen gevonden\n\n"
            for art in new_content[:10]:
                report += f"  [{art['type']}] {art['brand'].capitalize()}: {art['title'][:60]}\n"
            bot.reply_to(message, report)
        else:
            bot.reply_to(message, "✅ Geen nieuwe competitor content gevonden.")
        return

    if subcmd == "targets":
        bot.reply_to(message, "🎯 Skyscraper targets zoeken...")
        bot.send_chat_action(message.chat.id, 'typing')
        targets = find_skyscraper_targets()
        if targets:
            report = f"🎯 Top Skyscraper Targets:\n\n"
            for i, t in enumerate(targets[:10], 1):
                report += f"{i}. [{t['type']}] {t['competitor_title'][:55]}\n   → Slug: {t['suggested_slug']}\n"
            report += "\nGebruik /skyscraper <nummer> om het #1 target te overtreffen."
            bot.reply_to(message, report)
        else:
            bot.reply_to(message, "✅ We dekken alles wat concurrenten hebben! Goed bezig.")
        return

    # Default: full report
    bot.reply_to(message, "🕵️ Competitor rapport genereren...")
    bot.send_chat_action(message.chat.id, 'typing')
    report = generate_competitor_report()
    if len(report) > 4000:
        bot.reply_to(message, report[:4000])
        bot.reply_to(message, report[4000:])
    else:
        bot.reply_to(message, report)


@bot.message_handler(commands=['skyscraper'])
def cmd_skyscraper(message):
    """Schrijf een artikel dat beter is dan de concurrent."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔥 Skyscraper artikel schrijven...")
    bot.send_chat_action(message.chat.id, 'typing')

    targets = find_skyscraper_targets()
    if not targets:
        bot.reply_to(message, "Geen skyscraper targets gevonden. Gebruik eerst /spy scan.")
        return

    target = targets[0]
    bot.reply_to(message, f"✍️ Overtreffen: \"{target['competitor_title'][:60]}\"\nBrand: {target['brand'].capitalize()}\nType: {target['type']}\n\nDit kan 1-2 minuten duren...")

    ok, result = write_skyscraper_article(target)
    if ok:
        rebuild_sitemap()
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor Domination: {result}' && git push origin main")
        bot.reply_to(message, f"🔥 Skyscraper LIVE!\n\n📄 {result}\n🌐 https://aibuildermarketplace.com/b2b/{result}/\n\n💪 Beter dan: \"{target['competitor_title'][:50]}\"")
    else:
        bot.reply_to(message, f"❌ Skyscraper mislukt: {result}")


@bot.message_handler(commands=['clusters'])
def cmd_clusters(message):
    """Toon en bouw topic authority clusters."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    subcmd = parts[1].strip().lower() if len(parts) > 1 else "show"

    if subcmd == "build":
        bot.reply_to(message, "🏗️ Topic clusters bouwen + interne links toevoegen...")
        bot.send_chat_action(message.chat.id, 'typing')
        clusters = build_topic_clusters()
        fixed = apply_cluster_internal_links()
        if fixed > 0:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: cluster links ({fixed} articles)' && git push origin main")
        report = f"🏗️ Clusters gebouwd!\n\n"
        for brand, info in clusters.get("pillars", {}).items():
            report += f"📦 {info['display_name']}: {info['total_articles']} artikelen\n"
            report += f"   Pillar: {info['pillar_slug']}\n"
        report += f"\n🔗 Interne links toegevoegd aan {fixed} artikelen"
        bot.reply_to(message, report)
        return

    # Show clusters
    clusters = load_clusters()
    if not clusters.get("pillars"):
        clusters = build_topic_clusters()

    report = "🏗️ Topic Authority Clusters\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for brand, info in clusters.get("pillars", {}).items():
        report += f"📦 {info['display_name']}\n"
        report += f"   Pillar: {info['pillar_slug']}\n"
        report += f"   Artikelen: {info['total_articles']}\n"
        articles = info.get('articles', [])[:5]
        for a in articles:
            report += f"   → {a}\n"
        report += "\n"
    report += "Gebruik /clusters build om interne links toe te voegen."
    bot.reply_to(message, report)


@bot.message_handler(commands=['battles'])
def cmd_battles(message):
    """Toon ranking battles: welke artikelen stijgen/dalen."""
    if message.from_user.id != ADMIN_ID:
        return
    battles = load_battles()
    if not battles.get("active"):
        bot.reply_to(message, "⚔️ Nog geen ranking battles. Data komt zodra GSC snapshots beschikbaar zijn.")
        return

    report = "⚔️ Ranking Battles\n━━━━━━━━━━━━━━━━━━━━\n\n"

    # Top 10 artikelen
    top10 = [b for b in battles["active"] if b.get("current_position", 99) <= 10]
    if top10:
        report += f"🏆 Pagina 1 ({len(top10)} artikelen):\n"
        for b in sorted(top10, key=lambda x: x['current_position'])[:10]:
            trend = "📈" if b['current_position'] < b.get('start_position', 99) else "➡️"
            report += f"  {trend} #{b['current_position']:.0f} {b['slug'][:40]} ({b.get('clicks', 0)} clicks)\n"
        report += "\n"

    # Stijgers
    rising = [b for b in battles["active"]
              if b.get("current_position", 99) < b.get("start_position", 99)]
    if rising:
        report += f"📈 Stijgers ({len(rising)}):\n"
        for b in sorted(rising, key=lambda x: x['start_position'] - x['current_position'], reverse=True)[:5]:
            report += f"  #{b['current_position']:.0f} ← #{b['start_position']:.0f} {b['slug'][:35]}\n"
        report += "\n"

    # Dalers
    declining = [b for b in battles["active"] if b.get("status") == "declining"]
    if declining:
        report += f"📉 Actie nodig ({len(declining)}):\n"
        for b in declining[:5]:
            report += f"  #{b['current_position']:.0f} {b['slug'][:40]} — verbeter content!\n"

    # Wins
    if battles.get("won"):
        report += f"\n🏆 Gewonnen battles: {len(battles['won'])}\n"

    bot.reply_to(message, report)


@bot.message_handler(commands=['growth'])
def cmd_growth(message):
    """Volledig groeirapport: trends, winnaars, A/B tests, actieplan."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "📈 Growth rapport genereren...")
    bot.send_chat_action(message.chat.id, 'typing')
    report = generate_growth_report()
    # Split als te lang voor Telegram (max 4096 chars)
    if len(report) > 4000:
        bot.reply_to(message, report[:4000])
        bot.reply_to(message, report[4000:])
    else:
        bot.reply_to(message, report)


@bot.message_handler(commands=['abtest'])
def cmd_abtest(message):
    """Start of bekijk A/B tests op artikel titels."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or parts[1].strip().lower() == "status":
        # Toon status
        ab = load_ab_tests()
        report = "🔬 A/B Test Status\n━━━━━━━━━━━━━━━━━━━━\n\n"
        if ab.get("active"):
            report += f"Actief ({len(ab['active'])}):\n"
            for t in ab["active"]:
                report += f"  📊 {t['slug']}: variant {t['current_variant'].upper()}\n"
                report += f"     A: {t['variant_a']['title'][:50]}\n"
                report += f"     B: {t['variant_b']['title'][:50]}\n"
        else:
            report += "Geen actieve tests.\n"

        if ab.get("learnings"):
            report += f"\n💡 Learnings ({len(ab['learnings'])}):\n"
            for l in ab["learnings"][-3:]:
                report += f"  ✅ {l['slug']}: +{l['improvement']}% CTR\n"

        report += "\nGebruik: /abtest <slug>\nVictor genereert dan 2 titel-varianten en start de test."
        bot.reply_to(message, report)
        return

    # Start nieuwe test
    slug = parts[1].strip()
    article_path = f"{REPO_ROOT}/b2b/{slug}/index.html"
    if not os.path.isfile(article_path):
        bot.reply_to(message, f"❌ Artikel '{slug}' niet gevonden.")
        return

    bot.reply_to(message, f"🔬 A/B test voorbereiden voor {slug}...")
    bot.send_chat_action(message.chat.id, 'typing')

    # Lees huidige titel
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            html = f.read()
        title_match = re.search(r'<title>(.*?)</title>', html)
        current_title = title_match.group(1) if title_match else slug.replace('-', ' ').title()
    except:
        current_title = slug.replace('-', ' ').title()

    # Laat Claude een alternatieve titel genereren
    prompt = f"""Huidige artikel titel: "{current_title}"
Slug: {slug}

Genereer 1 alternatieve titel die waarschijnlijk een hogere CTR in Google heeft.
Gebruik een van deze bewezen patronen: vraag-formaat, nummer-lijst, "how to", power words (Ultimate, Complete, Best).
Max 60 karakters. Alleen de titel, geen uitleg."""

    try:
        res = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=100
        )
        alt_title = res.choices[0].message.content.strip().strip('"').strip("'")

        test, err = create_ab_test(slug, current_title, alt_title)
        if err:
            bot.reply_to(message, f"❌ {err}")
        else:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: A/B test started for {slug}' && git push origin main")
            bot.reply_to(message, f"🔬 A/B Test Gestart!\n\n📊 {slug}:\n  A: {current_title}\n  B: {alt_title}\n\nWissel elke {test['switch_every_days']} dagen. Winnaar na {test['min_impressions']} impressies per variant.")
    except Exception as e:
        bot.reply_to(message, f"❌ Kon geen alternatieve titel genereren: {e}")


@bot.message_handler(commands=['plan'])
def cmd_plan(message):
    """Smart article planner: data-driven content planning."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "📋 Smart content plan genereren...")
    bot.send_chat_action(message.chat.id, 'typing')

    plan = smart_article_planner()
    if plan:
        report = "📋 Data-Driven Content Plan\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, item in enumerate(plan, 1):
            icon = "🔴" if item['priority'] == 'HIGH' else "🟡"
            report += f"{i}. {icon} {item['action']}\n"
        report += "\n💡 Gebaseerd op GSC data, winning patterns, en content gaps."
        bot.reply_to(message, report)
    else:
        bot.reply_to(message, "📋 Geen data beschikbaar voor planning. Gebruik eerst /gsc fetch en /research.")


@bot.message_handler(commands=['gsc'])
def cmd_gsc(message):
    """Google Search Console data ophalen en analyseren."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    subcmd = parts[1].strip().lower() if len(parts) > 1 else "report"

    if subcmd == "setup":
        bot.reply_to(message, setup_gsc())
        return

    if subcmd == "fetch":
        bot.reply_to(message, "📊 GSC data ophalen...")
        bot.send_chat_action(message.chat.id, 'typing')
        data, err = fetch_gsc_data()
        if err:
            bot.reply_to(message, f"❌ {err}")
            return
        report = f"📊 GSC Data ({data['period']})\n━━━━━━━━━━━━━━━━━━━━\n\n"
        report += f"📈 Top pagina's (clicks):\n"
        for p in data['pages'][:10]:
            report += f"  {p['clicks']} clicks | {p['impressions']} imp | pos {p['position']} | {p['page'].split('/')[-2] if '/b2b/' in p['page'] else p['page'][-30:]}\n"
        report += f"\n🔍 Top queries:\n"
        for q in data['queries'][:10]:
            report += f"  {q['impressions']} imp | {q['clicks']} clicks | pos {q['position']} | {q['query']}\n"
        bot.reply_to(message, report)
        return

    # Default: insights
    bot.reply_to(message, "🔍 GSC insights analyseren...")
    bot.send_chat_action(message.chat.id, 'typing')
    insights = get_gsc_insights()
    if isinstance(insights, str):
        bot.reply_to(message, insights)
    elif insights:
        report = "🔍 GSC Insights\n━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(insights)
        bot.reply_to(message, report)
    else:
        bot.reply_to(message, "✅ Geen urgente content gaps gevonden. Gebruik /gsc fetch voor ruwe data.")


@bot.message_handler(commands=['sitemap'])
def cmd_sitemap(message):
    """Rebuild sitemap.xml en robots.txt."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🗺️ Sitemap rebuilden...")

    save_task("sitemap_rebuild", "sitemap", "Sitemap + robots.txt rebuild")
    count = rebuild_sitemap()
    rebuild_robots_txt()
    run_command(f"cd {REPO_ROOT} && git add sitemap.xml robots.txt && git commit -m 'Victor: rebuilt sitemap ({count} URLs)' && git push origin main")
    complete_task("sitemap_rebuild")
    bot.reply_to(message, f"✅ Sitemap gerebuild met {count} URLs + robots.txt bijgewerkt en gepusht!")


@bot.message_handler(commands=['ogimages'])
def cmd_ogimages(message):
    """Genereer OG images voor alle artikelen."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🖼️ OG images genereren voor alle artikelen...\nDit kan even duren.")
    bot.send_chat_action(message.chat.id, 'typing')

    save_task("og_images", "og_images", "OG images genereren")
    generated, errors = generate_all_og_images()
    if generated > 0:
        # Rebuild sitemap want artikelen zijn gewijzigd
        rebuild_sitemap()
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: generated {generated} OG images' && git push origin main")
    complete_task("og_images")
    bot.reply_to(message, f"🖼️ OG Images Rapport:\n  ✅ Gegenereerd: {generated}\n  ❌ Errors: {errors}\n  📦 Gepusht naar GitHub")


@bot.message_handler(commands=['keywords'])
def cmd_keywords(message):
    """Toon keyword gaps en suggesties voor nieuwe artikelen."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔑 Content gaps analyseren...")
    bot.send_chat_action(message.chat.id, 'typing')

    suggestions = suggest_next_articles(10)
    if suggestions:
        report = "🔑 Top Artikel Suggesties (hoogste impact eerst)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, s in enumerate(suggestions, 1):
            report += f"{i}. {s}\n"
        report += "\nGebruik /generate om het top-artikel te schrijven."
        bot.reply_to(message, report)
    else:
        bot.reply_to(message, "✅ Goede coverage! Geen urgente content gaps gevonden.")


@bot.message_handler(commands=['tasks'])
def cmd_tasks(message):
    """Toon lopende en afgebroken taken."""
    if message.from_user.id != ADMIN_ID:
        return
    tasks = load_tasks()
    if not tasks:
        bot.reply_to(message, "📋 Geen taken in het systeem.")
        return

    report = "📋 Taak Overzicht\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for tid, task in sorted(tasks.items(), key=lambda x: x[1].get('updated_at', ''), reverse=True)[:10]:
        icon = {"running": "🔄", "completed": "✅", "failed": "❌"}.get(task['state'], "❓")
        report += f"{icon} {task['description'][:50]} ({task['state']})\n   {task.get('started_at', '?')}\n"
    bot.reply_to(message, report)


@bot.message_handler(commands=['autopilot'])
def cmd_autopilot(message):
    """Autopilot status: sprint, chain reactions, predictions."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🤖 Autopilot status ophalen...")
    bot.send_chat_action(message.chat.id, 'typing')

    ap = load_autopilot()
    sprint = load_sprint()

    msg = "🤖 Victor Autopilot Engine\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Chain reactions
    chains = ap.get("chain_reactions", [])
    if chains:
        msg += f"⚡ Chain Reactions ({len(chains)} triggers):\n"
        for c in chains[-5:]:
            msg += f"  - {c.get('slug', '?')}: {c.get('event', '?')} → {len(c.get('actions', []))} acties\n"
    else:
        msg += "⚡ Chain Reactions: nog geen triggers\n"

    # Sprint
    msg += f"\n📋 Sprint: {sprint.get('current_week', 'niet actief')}\n"
    planned = sprint.get("planned_tasks", [])
    completed = sprint.get("completed_tasks", [])
    msg += f"  Gepland: {len(planned)} | Gedaan: {len(completed)}\n"
    if planned:
        for t in planned[:3]:
            msg += f"  → {t.get('type', '?')}: {t.get('target', '?')[:40]} (prio {t.get('priority', '?')})\n"

    # Recycled
    recycled = ap.get("recycled_articles", [])
    msg += f"\n♻️ Gerecycled: {len(recycled)} artikelen\n"

    # Predictions
    predictions = ap.get("predictions", [])
    if predictions:
        msg += f"\n🎯 Laatste Voorspellingen:\n"
        for p in predictions[-5:]:
            msg += f"  - {p.get('keyword', '?')[:35]}: {p.get('score', '?')}% kans\n"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['predict'])
def cmd_predict(message):
    """Voorspel ranking succes voor een keyword/brand."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /predict <keyword> [brand]\nVoorbeeld: /predict synthesia-review Synthesia")
        return

    keyword = parts[1]
    brand = parts[2] if len(parts) > 2 else keyword.split('-')[0].capitalize()

    bot.send_chat_action(message.chat.id, 'typing')
    score, factors = predict_ranking_success(keyword, brand)

    # Save prediction
    ap = load_autopilot()
    ap.setdefault("predictions", []).append({
        "keyword": keyword,
        "brand": brand,
        "score": score,
        "factors": factors,
        "date": str(datetime.now().date())
    })
    ap["predictions"] = ap["predictions"][-50:]
    save_autopilot(ap)

    emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
    msg = f"🎯 Ranking Voorspelling: {keyword}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{emoji} Score: {score}/100\n\n"
    msg += "📊 Factoren:\n"
    for f in factors:
        msg += f"  - {f}\n"

    if score >= 70:
        msg += "\n✅ Sterke kans op pagina 1! Ga ervoor."
    elif score >= 40:
        msg += "\n⚠️ Kan lukken, maar vergt extra effort (clusters, backlinks)."
    else:
        msg += "\n❌ Lastig. Overweeg een niche-variatie of ander keyword."

    bot.reply_to(message, msg)


@bot.message_handler(commands=['sprint'])
def cmd_sprint(message):
    """Sprint status of plan nieuwe sprint."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "status"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "plan":
        bot.reply_to(message, "📋 Nieuwe sprint plannen...")
        plan_weekly_sprint()
        sprint = load_sprint()
        msg = f"📋 Sprint {sprint['current_week']} — Gepland!\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, t in enumerate(sprint.get("planned_tasks", []), 1):
            msg += f"{i}. [{t['type']}] {t['target'][:45]} (prio: {t['priority']})\n"
        bot.reply_to(message, msg)

    elif action == "run":
        bot.reply_to(message, "⚡ Sprint taak uitvoeren...")
        result = execute_sprint_tasks()
        bot.reply_to(message, f"📋 Sprint Resultaat:\n\n{result}")

    else:
        sprint = load_sprint()
        msg = f"📋 Sprint Status: {sprint.get('current_week', 'niet actief')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        planned = sprint.get("planned_tasks", [])
        completed = sprint.get("completed_tasks", [])
        msg += f"📌 Gepland: {len(planned)} taken\n"
        msg += f"✅ Gedaan: {len(completed)} taken\n\n"

        if planned:
            msg += "📌 Te doen:\n"
            for t in planned[:5]:
                msg += f"  → [{t['type']}] {t['target'][:40]} (prio: {t['priority']})\n"

        if completed:
            msg += "\n✅ Afgerond:\n"
            for t in completed[-5:]:
                msg += f"  ✓ [{t['type']}] {t['target'][:40]}\n"

        # Sprint history
        history = sprint.get("history", [])
        if history:
            msg += f"\n📈 Vorige sprints: {len(history)} weken"
            last = history[-1]
            msg += f"\n  Laatste: {last.get('week', '?')} — {last.get('completed', 0)}/{last.get('planned', 0)} taken"

        bot.reply_to(message, msg)


@bot.message_handler(commands=['briefing'])
def cmd_briefing(message):
    """Dagelijks briefing rapport."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "☀️ Briefing genereren...")
    bot.send_chat_action(message.chat.id, 'typing')
    briefing = generate_daily_briefing()
    bot.reply_to(message, briefing)


@bot.message_handler(commands=['programmatic'])
def cmd_programmatic(message):
    """Programmatic SEO: genereer mass pages."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "status"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "generate":
        bot.reply_to(message, "🏭 Programmatic pagina's genereren...")
        generated, total = programmatic_batch(max_pages=3)
        if generated:
            msg = f"🏭 Programmatic SEO — {len(generated)} pagina's gegenereerd!\n\n"
            msg += "\n".join(f"  ✅ {s}" for s in generated)
            msg += f"\n\n📊 Nog {total - len(generated)} combinaties mogelijk"
        else:
            msg = f"🏭 Alle {total} combinaties zijn al gegenereerd! 🎉"
        bot.reply_to(message, msg)
    else:
        combos = generate_programmatic_combinations()
        b2b_path = f"{REPO_ROOT}/b2b"
        existing = sum(1 for c in combos if os.path.exists(f"{b2b_path}/{c['slug']}.html"))
        prog = load_programmatic()

        msg = f"🏭 Programmatic SEO Status\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"📊 Totaal combinaties: {len(combos)}\n"
        msg += f"✅ Gegenereerd: {existing}\n"
        msg += f"📝 Te doen: {len(combos) - existing}\n\n"

        by_type = {}
        for c in combos:
            by_type[c["type"]] = by_type.get(c["type"], 0) + 1
        msg += "📋 Per type:\n"
        for t, count in by_type.items():
            done = prog.get("stats", {}).get(t, 0)
            msg += f"  {t}: {done}/{count}\n"

        msg += f"\nGebruik /programmatic generate om 3 pagina's te genereren."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['schema'])
def cmd_schema(message):
    """Schema markup toevoegen aan artikelen."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "status"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "add":
        bot.reply_to(message, "🏷️ Schema markup toevoegen...")
        done, total = schema_batch(max_articles=5)
        if done:
            msg = f"🏷️ Schema toegevoegd aan {len(done)} artikelen:\n\n"
            msg += "\n".join(f"  ✅ {s}" for s in done)
        else:
            msg = f"🏷️ Alle {total} artikelen hebben al schema markup!"
        bot.reply_to(message, msg)
    else:
        sd = load_schema_data()
        msg = f"🏷️ Schema Markup Status\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"✅ Artikelen met schema: {len(sd.get('articles_with_schema', []))}\n"
        types = sd.get("schema_types", {})
        if types:
            msg += "\n📋 Per type:\n"
            for t, count in types.items():
                msg += f"  {t}: {count}\n"
        msg += f"\nGebruik /schema add om schema toe te voegen."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['syndicate'])
def cmd_syndicate(message):
    """Multi-channel syndicatie."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)

    bot.send_chat_action(message.chat.id, 'typing')

    if len(parts) > 1 and parts[1] == "run":
        bot.reply_to(message, "📢 Syndication content genereren...")
        results = syndication_cycle(max_articles=2)
        if results:
            msg = f"📢 Syndication — {len(results)} artikelen verwerkt:\n\n"
            msg += "\n".join(f"  ✅ {r}" for r in results)
        else:
            msg = "📢 Geen nieuwe artikelen om te syndiceren."
        bot.reply_to(message, msg)
    else:
        synd = load_syndication()
        msg = f"📢 Multi-Channel Syndicatie\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"📊 Gesyndiceerd: {len(synd.get('syndicated', []))} artikelen\n"
        platforms = synd.get("platforms", {})
        if platforms:
            msg += "\n📋 Per platform:\n"
            for p, count in platforms.items():
                msg += f"  {p}: {count}\n"
        msg += f"\nGebruik /syndicate run om content te genereren."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['linkgraph'])
def cmd_linkgraph(message):
    """Internal link graph analyse."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "scan"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "fix":
        bot.reply_to(message, "🔗 Interne links fixen...")
        fixed = auto_fix_internal_links(max_fixes=5)
        if fixed:
            msg = f"🔗 {len(fixed)} link fixes toegepast:\n\n"
            msg += "\n".join(f"  ✅ {f}" for f in fixed)
        else:
            msg = "🔗 Geen link problemen gevonden!"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🔗 Link graph scannen...")
        recs = generate_link_recommendations()
        lg = load_linkgraph()
        pages = lg.get("pages", {})

        msg = f"🔗 Internal Link Graph\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"📊 Totaal pagina's: {len(pages)}\n"

        orphans = sum(1 for p, d in pages.items() if d.get("in", 0) == 0)
        dead_ends = sum(1 for p, d in pages.items() if d.get("out", 0) == 0)
        msg += f"🚨 Orphan pagina's (geen incoming): {orphans}\n"
        msg += f"🔚 Dead-end pagina's (geen outgoing): {dead_ends}\n\n"

        # Top scored pages
        sorted_pages = sorted(pages.items(), key=lambda x: x[1].get("score", 0), reverse=True)
        if sorted_pages:
            msg += "🏆 Sterkste pagina's:\n"
            for slug, data in sorted_pages[:5]:
                msg += f"  {slug[:30]}: score {data['score']} (in:{data['in']} out:{data['out']})\n"

        if recs:
            msg += f"\n⚠️ {len(recs)} aanbevelingen:\n"
            for r in recs[:5]:
                msg += f"  - {r['action'][:60]}\n"

        msg += f"\nGebruik /linkgraph fix om problemen automatisch op te lossen."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['serp'])
def cmd_serp(message):
    """SERP positie tracking."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "report"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "update":
        bot.reply_to(message, "📊 SERP posities updaten...")
        alerts = update_serp_tracking()
        if alerts:
            msg = "📊 SERP Updates:\n\n" + "\n".join(f"  {a}" for a in alerts)
        else:
            msg = "📊 SERP tracking bijgewerkt — geen grote veranderingen."
        bot.reply_to(message, msg)
    else:
        report = generate_serp_report()
        bot.reply_to(message, report)


@bot.message_handler(commands=['domination'])
def cmd_domination(message):
    """Volledige Domination Matrix cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔥 Domination Matrix cyclus starten...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = domination_matrix_cycle()
    if actions:
        msg = "🔥 Domination Matrix — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "🔥 Domination Matrix: geen acties nodig."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['restyle'])
def cmd_restyle(message):
    """Restyle alle artikelen naar dark theme met SVG brand logos via fix_articles.py."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🎨 Alle artikelen restylen naar dark theme met brand logos...")
    bot.send_chat_action(message.chat.id, 'typing')

    # Gebruik fix_articles.py — dezelfde kwaliteit als handmatig
    fix_script = "/root/felix_hq/fix_articles.py"
    if not os.path.exists(fix_script):
        fix_script = f"{REPO_ROOT}/fix_articles.py"
    if not os.path.exists(fix_script):
        bot.reply_to(message, "❌ fix_articles.py niet gevonden. Upload het eerst naar /root/felix_hq/")
        return

    result = run_command(f"cd {REPO_ROOT} && python3 {fix_script}", timeout=120)
    bot.reply_to(message, f"📋 {result}")

    # Git commit en push
    git_result = run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: restyled all articles to dark theme' && git push origin main")
    if "nothing to commit" in git_result:
        bot.reply_to(message, "✅ Alle artikelen hadden al het juiste dark theme!")
    elif "error" in git_result.lower() or "rejected" in git_result.lower():
        # Probeer force push als rebase faalt
        git_result2 = run_command(f"cd {REPO_ROOT} && git push origin main --force")
        bot.reply_to(message, f"✅ Restyled en gepusht (force)!\n{git_result2[:200]}")
    else:
        bot.reply_to(message, "✅ Alle artikelen gerestyled en live gepusht!")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, """Victor 11.0 Domination Matrix — Commando's:

📊 Monitoring:
/status — Systeem status
/logs — Cron output
/uptime — Website bereikbaarheid
/articles — Artikel overzicht
/tasks — Lopende/afgebroken taken

🔍 Analyse:
/seo — SEO gezondheidscheck
/affcheck — Affiliate link check
/linkcheck — Test alle affiliate URLs
/quality — Artikelkwaliteit analyse
/strategy — AI strategisch advies

🧠 Self-Learning:
/brain — Toon geleerde kennis & patronen
/diagnose — Self-analyse + verbeterpunten
/research — Web scan: competitors, affiliate links

📈 SEO & Data:
/gsc [setup|fetch] — Google Search Console data
/keywords — Content gaps + artikel suggesties
/sitemap — Rebuild sitemap.xml
/ogimages — OG images voor social sharing

💰 Revenue Intelligence:
/revenue — Revenue rapport + geschatte earnings
/roi — Hoogste ROI acties
/funnels [build] — Conversion funnels
/dashboard — Live admin dashboard genereren
/social [slug] — Social media content genereren

🚀 Growth Engine:
/growth — Groeirapport met trends
/abtest [slug] — A/B tests op titels
/plan — Data-driven content planning

🕵️ Competitor Domination:
/spy [scan|targets] — Competitor intelligence
/skyscraper — Overtref de concurrent
/clusters [build] — Topic authority clusters
/battles — Ranking battles tracker

🤖 Autopilot Engine:
/autopilot — Autopilot status & chain reactions
/predict <keyword> [brand] — Ranking voorspelling
/sprint [plan|run] — Wekelijkse sprint
/briefing — Dagelijks ochtend briefing

🔥 Domination Matrix:
/programmatic [generate] — Mass page generation
/schema [add] — Rich snippets toevoegen
/syndicate [run] — Multi-channel content
/linkgraph [fix] — Internal link analyse
/serp [update] — Positie tracking & alerts
/domination — Volledige cyclus draaien

🛠️ Actie:
/generate — Genereer een artikel
/improve — Verbeter het slechtste artikel
/autofix — Auto-improve batch
/optimize — Interne links
/fix <probleem> — Los op tot het werkt
/write <taak> — Schrijf code
/multifile <taak> — Multi-file refactor

🎨 Design:
/redesign <pagina> — Professionele pagina
/restyle — Dark theme + SVG logos

📸 Foto/document → AI vision analyse
Of stuur een bericht — ik pak het op.""")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Verwerk foto's: download, stuur naar Claude vision, en reageer."""
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_chat_action(message.chat.id, 'typing')
    caption = message.caption or "Wat zie je op deze afbeelding? Analyseer het en geef feedback."
    log(f"USER PHOTO: {caption}")

    # Pak de grootste versie van de foto
    photo = message.photo[-1]  # Laatste = hoogste resolutie
    file_data, file_path = download_telegram_file(photo.file_id)
    if not file_data:
        bot.reply_to(message, "❌ Kon de foto niet downloaden.")
        return

    # Base64 encode voor Claude vision
    img_base64 = base64.b64encode(file_data).decode('utf-8')
    mime_type = "image/jpeg"

    history = load_memory()
    history.append({"role": "user", "content": f"[Foto gestuurd] {caption}"})

    reply = ask_victor_with_image(caption, img_base64, mime_type, history[:-1])
    log(f"VICTOR (photo): {reply[:300]}")

    # Als Victor commando's wil uitvoeren, doe dat
    if "COMMANDO:" in reply:
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        commands = [p.split("\n")[0].strip().strip('`')
                    for p in reply.split("COMMANDO:")[1:]
                    if p.split("\n")[0].strip()][:2]
        for cmd in commands:
            bot.reply_to(message, f"🛠 `{cmd}`")
            out = run_command(cmd)
            bot.reply_to(message, f"📋 {out}")
    else:
        bot.reply_to(message, reply)

    history.append({"role": "assistant", "content": reply})
    save_memory(history)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Verwerk documenten: download, lees inhoud, stuur naar Victor."""
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_chat_action(message.chat.id, 'typing')
    doc = message.document
    caption = message.caption or f"Ik stuur je dit bestand: {doc.file_name}. Analyseer het."
    log(f"USER DOC: {doc.file_name} ({doc.file_size} bytes) - {caption}")

    file_data, file_path = download_telegram_file(doc.file_id)
    if not file_data:
        bot.reply_to(message, "❌ Kon het bestand niet downloaden.")
        return

    fname = doc.file_name or "bestand"
    ext = os.path.splitext(fname)[1].lower()

    # Afbeeldingen → vision
    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        img_base64 = base64.b64encode(file_data).decode('utf-8')
        mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif', '.webp': 'image/webp'}
        mime = mime_map.get(ext, 'image/jpeg')

        history = load_memory()
        history.append({"role": "user", "content": f"[Afbeelding: {fname}] {caption}"})
        reply = ask_victor_with_image(caption, img_base64, mime, history[:-1])
        bot.reply_to(message, reply)
        history.append({"role": "assistant", "content": reply})
        save_memory(history)
        return

    # Tekstbestanden → lees inhoud en stuur naar Victor
    text_content = None
    if ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv', '.xml',
               '.yaml', '.yml', '.sh', '.bash', '.env', '.conf', '.ini', '.log', '.sql']:
        try:
            text_content = file_data.decode('utf-8', errors='replace')[:8000]
        except:
            text_content = None

    # Sla bestand op in /root/felix_hq/uploads/
    upload_dir = "/root/felix_hq/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, fname)
    with open(save_path, 'wb') as f:
        f.write(file_data)

    history = load_memory()

    if text_content:
        user_msg = f"[Bestand: {fname}]\n{caption}\n\n--- INHOUD ---\n{text_content}"
    else:
        user_msg = f"[Bestand: {fname}, {doc.file_size} bytes, opgeslagen als {save_path}]\n{caption}"

    history.append({"role": "user", "content": user_msg})
    bot.reply_to(message, f"📁 {fname} ontvangen ({doc.file_size} bytes). Ik analyseer het...")

    reply = ask_victor(user_msg, history[:-1])
    log(f"VICTOR (doc): {reply[:300]}")

    # Voer commando's uit als Victor dat wil
    if "COMMANDO:" in reply:
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        commands = [p.split("\n")[0].strip().strip('`')
                    for p in reply.split("COMMANDO:")[1:]
                    if p.split("\n")[0].strip()][:2]
        for cmd in commands:
            bot.reply_to(message, f"🛠 `{cmd}`")
            out = run_command(cmd)
            bot.reply_to(message, f"📋 {out}")
    else:
        bot.reply_to(message, reply)

    history.append({"role": "assistant", "content": reply})
    save_memory(history)


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_text = message.text.strip()
    log(f"USER: {user_text}")
    bot.send_chat_action(message.chat.id, 'typing')

    history = load_memory()
    history.append({"role": "user", "content": user_text})

    # Auto-continue loop: Victor blijft doorgaan zolang er commando's nodig zijn
    MAX_ROUNDS = 20  # veiligheidsgrens
    current_input = user_text
    round_num = 0

    while round_num < MAX_ROUNDS:
        round_num += 1

        if round_num == 1:
            reply = ask_victor(current_input, history[:-1])
        else:
            bot.send_chat_action(message.chat.id, 'typing')
            reply = ask_victor(current_input, history)

        log(f"VICTOR [ronde {round_num}]: {reply[:300]}")

        if "COMMANDO:" not in reply:
            # Geen commando's meer → stuur antwoord en stop
            bot.reply_to(message, reply)
            history.append({"role": "assistant", "content": reply})
            break

        # Er zijn commando's — voer ze uit
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        commands = [p.split("\n")[0].strip().strip('`')
                    for p in reply.split("COMMANDO:")[1:]
                    if p.split("\n")[0].strip()][:2]

        all_output = []
        for cmd in commands:
            bot.reply_to(message, f"🛠 [{round_num}] `{cmd}`")
            output = run_command(cmd)
            bot.reply_to(message, f"📋 {output}")
            all_output.append(f"$ {cmd}\n{output}")
            time.sleep(0.5)

        # Geheugen bijwerken
        history.append({"role": "assistant", "content": reply})
        combined = "\n".join(all_output)[:1500]
        history.append({"role": "user", "content": f"[Output ronde {round_num}]:\n{combined}"})

        # Vraag Victor: klaar, of moet je door?
        current_input = f"""Output van ronde {round_num}:\n{combined}

Analyseer dit resultaat. Je hebt drie opties:
1. Als alles GELUKT is: geef een korte bevestiging. Geen COMMANDO:.
2. Als er een FOUT is die je kunt fixen: leg kort uit wat je gaat doen en gebruik COMMANDO: voor de fix.
3. Als je meer info nodig hebt om verder te gaan: gebruik COMMANDO: om die info op te halen.

Ga door tot het probleem ECHT opgelost is. Geef tussen elke stap een korte status update."""

    else:
        # Veiligheidsgrens bereikt
        bot.reply_to(message, f"⚠️ {MAX_ROUNDS} rondes uitgevoerd. Ik stop hier om een oneindige loop te voorkomen. Stuur me een bericht als ik verder moet gaan.")
        history.append({"role": "assistant", "content": f"Gestopt na {MAX_ROUNDS} rondes."})

    save_memory(history)

# ── STATUS RAPPORT ──────────────────────────────────────────────────────────
def generate_status_report():
    articles = run_command(f"ls {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | wc -l")
    last = run_command(f"ls -t {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | head -3")
    cron_status = run_command("tail -5 /root/felix_hq/cron.log | grep -E 'Succes|rejected|error'")
    git_status = run_command(f"cd {REPO_ROOT} && git log --oneline -3")
    uptime = run_command("uptime -p")
    disk = run_command("df -h / | tail -1 | awk '{print $5}'")

    return f"""📊 Victor 11.0 Domination Matrix — Status Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
⏱ {uptime}
💾 Disk: {disk}
📝 Artikelen: {articles.strip()}
🆕 Laatste: {last}
📦 Git: {git_status}
⚙️ Cron: {cron_status or 'Geen recente output'}
🤖 Model: {MODEL}"""

# ── MONITORING & OPTIMALISATIE ──────────────────────────────────────────────
def check_uptime():
    """Ping de website en check of hij online is."""
    urls = [
        ("Homepage", "https://aibuildermarketplace.com/"),
        ("B2B pagina", "https://aibuildermarketplace.com/b2b/"),
    ]
    results = []
    for name, url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Victor-Monitor/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            code = resp.getcode()
            if code == 200:
                results.append((name, "OK", code))
            else:
                results.append((name, "WARN", code))
        except Exception as e:
            results.append((name, "DOWN", str(e)[:100]))
    return results


def check_affiliate_links():
    """Check of alle affiliate URLs nog werken."""
    results = []
    for brand, url in VAULT.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Victor-LinkCheck/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            code = resp.getcode()
            results.append(f"  {brand}: {'✅' if code < 400 else '❌'} ({code})")
        except Exception as e:
            results.append(f"  {brand}: ⚠️ ({str(e)[:50]})")
    return results


def check_article_quality():
    """Analyseer artikelkwaliteit: lengte, meta tags, interne links."""
    issues = []
    b2b_path = f"{REPO_ROOT}/b2b"

    for folder in os.listdir(b2b_path):
        article_path = os.path.join(b2b_path, folder, "index.html")
        if not os.path.isfile(article_path):
            continue
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                html = f.read()
            size = len(html)
            has_meta_desc = 'meta name="description"' in html or "meta name='description'" in html
            has_og = 'og:image' in html
            has_affiliate = 'nofollow sponsored' in html
            has_internal = '/b2b/' in html and 'Read more' in html

            # Te kort artikel (< 3KB is waarschijnlijk leeg of broken)
            if size < 3000:
                issues.append(f"  ⚠️ {folder}: te kort ({size} bytes)")
            # Geen meta description
            if not has_meta_desc:
                issues.append(f"  📝 {folder}: geen meta description")
            # Geen affiliate link
            if not has_affiliate:
                issues.append(f"  💰 {folder}: geen affiliate link")
        except:
            pass

    return issues[:20]  # max 20 issues tonen


def optimize_internal_links():
    """Voeg interne links toe aan artikelen die er geen hebben."""
    b2b_path = f"{REPO_ROOT}/b2b"
    folders = [f for f in os.listdir(b2b_path) if os.path.isdir(os.path.join(b2b_path, f))
               and f not in ['sitemap.xml']]
    fixed = 0

    for folder in folders:
        article_path = os.path.join(b2b_path, folder, "index.html")
        if not os.path.isfile(article_path):
            continue
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Check of er al interne links zijn
            if 'Read more B2B Insights' in html or 'read-more-links' in html:
                continue

            # Vind gerelateerde artikelen (zelfde tool)
            tool = folder.split('-')[0].lower()
            related = [f for f in folders if f.lower().startswith(tool) and f != folder][:3]
            if not related:
                related = [f for f in folders if f != folder][:3]

            links_html = "".join([
                f"<li><a href='/b2b/{r}/' style='color:#58a6ff;text-decoration:none'>{r.replace('-', ' ').title()}</a></li>"
                for r in related
            ])
            internal_block = f"""<div id='read-more-links' style='margin-top:30px;padding:20px;background:#161b22;border:1px solid #30363d;border-radius:10px;'>
<h4 style='color:#e6edf3;margin-top:0;'>Read more B2B Insights:</h4>
<ul style='list-style:none;padding:0;'>{links_html}</ul>
</div>"""

            # Voeg toe voor </body>
            if '</body>' in html:
                html = html.replace('</body>', f"{internal_block}\n</body>")
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                fixed += 1
        except:
            pass

    return fixed


def find_worst_articles(n=5):
    """Vind de N slechtste artikelen op basis van grootte."""
    b2b_path = f"{REPO_ROOT}/b2b"
    articles = []
    for folder in os.listdir(b2b_path):
        article_path = os.path.join(b2b_path, folder, "index.html")
        if os.path.isfile(article_path):
            size = os.path.getsize(article_path)
            articles.append((folder, size))
    articles.sort(key=lambda x: x[1])
    return articles[:n]


# ── PROACTIEVE SCHEDULER ────────────────────────────────────────────────────
def auto_fix_git():
    """Fix git problemen automatisch."""
    fixes = []
    # Check en fix lock files
    for lockfile in [f"{REPO_ROOT}/.git/index.lock", f"{REPO_ROOT}/.git/HEAD.lock"]:
        check = run_command(f"test -f {lockfile} && echo EXISTS")
        if "EXISTS" in check:
            run_command(f"rm -f {lockfile}")
            fixes.append(f"Removed {lockfile}")

    # Check git status
    status = run_command(f"cd {REPO_ROOT} && git status --porcelain")
    if status and status != "(geen output)":
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: auto-commit pending changes'")
        fixes.append("Auto-committed pending changes")

    # Try to push
    push_result = run_command(f"cd {REPO_ROOT} && git pull --rebase origin main && git push origin main")
    if "rejected" in push_result or "conflict" in push_result.lower():
        # Force rebase met ours strategy
        run_command(f"cd {REPO_ROOT} && git rebase --abort 2>/dev/null; git checkout --theirs . 2>/dev/null; git pull --rebase origin main && git push origin main")
        fixes.append(f"Fixed git conflict: {push_result[:200]}")
    elif "error" in push_result.lower() or "fatal" in push_result.lower():
        fixes.append(f"Git push issue: {push_result[:200]}")
    else:
        fixes.append("Git sync OK")

    return fixes

def check_article_pipeline():
    """Check of artikelen gegenereerd worden en fix als nodig."""
    problems = []
    fixes = []

    # Check of cron draait
    cron_status = run_command("systemctl is-active cron")
    if "active" not in cron_status:
        run_command("systemctl start cron")
        fixes.append("Cron was gestopt — herstart")

    # Check crontab entry
    crontab = run_command("crontab -l 2>/dev/null")
    if "generate_article" not in crontab:
        problems.append("⚠️ generate_article.py staat NIET in crontab!")

    # Check laatste artikel (meest recent gewijzigde folder)
    latest = run_command(f"ls -t {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | head -1")
    latest_time = run_command(f"stat -c %Y {REPO_ROOT}/b2b/{latest.strip()}/index.html 2>/dev/null")
    try:
        age_hours = (time.time() - int(latest_time.strip())) / 3600
        if age_hours > 4:
            problems.append(f"⚠️ Laatste artikel is {age_hours:.0f} uur oud — zou max 2 uur moeten zijn")
            # Probeer handmatig te genereren
            log("Auto-generating article because pipeline seems stuck")
            gen_out = run_command("/root/felix_hq/venv/bin/python3 /root/felix_hq/generate_article.py", timeout=120)
            if "Succes" in gen_out or "succes" in gen_out:
                fixes.append("Auto-generated article (pipeline was stuck)")
            else:
                problems.append(f"Auto-generate failed: {gen_out[:300]}")
    except:
        pass

    # Check cron.log voor errors
    cron_log = run_command("tail -10 /root/felix_hq/cron.log 2>/dev/null")
    if "rejected" in cron_log:
        git_fixes = auto_fix_git()
        fixes.extend(git_fixes)
    if "error" in cron_log.lower() and "rejected" not in cron_log:
        problems.append(f"Errors in cron.log: {cron_log[:200]}")

    return problems, fixes

def generate_weekly_strategy():
    """Wekelijks strategisch rapport met AI-analyse."""
    data = {}
    data['total'] = run_command(f"ls {REPO_ROOT}/b2b/ | grep -v index | grep -v sitemap | wc -l").strip()
    for brand in ['kinsta', 'synthesia', 'invideo', 'replit', 'bitvavo', 'murf']:
        data[brand] = run_command(f"ls {REPO_ROOT}/b2b/ | grep '^{brand}' | wc -l").strip()
    data['new_7d'] = run_command(f"find {REPO_ROOT}/b2b/ -maxdepth 2 -name 'index.html' -mtime -7 | wc -l").strip()
    data['disk'] = run_command("df -h / | tail -1 | awk '{print $5}'").strip()

    prompt = f"""Schrijf een kort wekelijks strategierapport (max 250 woorden, Nederlands) voor AIBuilder Marketplace:

Data:
- Totaal artikelen: {data['total']} (waarvan {data['new_7d']} nieuw deze week)
- Kinsta: {data['kinsta']}, Synthesia: {data['synthesia']}, InVideo: {data['invideo']}
- Replit: {data['replit']}, Bitvavo: {data['bitvavo']}, Murf: {data['murf']}
- Disk: {data['disk']}

Geef:
1. Score deze week (1-10)
2. Wat ging goed
3. Wat moet beter
4. Top 3 acties voor komende week (concreet, specifiek)
5. Revenue tip"""

    return ask_victor(prompt, [])


def proactive_loop():
    """Elke 15 min: check pipeline + fix problemen. Rapport 2x per dag + wekelijks strategie.
    Extra: dagelijkse web research en wekelijkse auto-improve."""
    last_report = None
    last_check = None
    last_weekly = None
    last_research = None
    last_auto_improve = None
    while True:
        try:
            now = datetime.now()
            hour = now.hour
            weekday = now.weekday()  # 0=maandag

            # Health check elke 15 minuten
            if last_check is None or (now - last_check) > timedelta(minutes=15):
                problems, fixes = check_article_pipeline()
                last_check = now

                if fixes:
                    log(f"Auto-fixes: {', '.join(fixes)}")
                if problems:
                    log(f"Problems detected: {', '.join(problems)}")
                    try:
                        alert = "🚨 Victor Auto-Monitor:\n\n"
                        if fixes:
                            alert += "✅ Auto-fixed:\n" + "\n".join(f"  - {f}" for f in fixes) + "\n\n"
                        alert += "⚠️ Needs attention:\n" + "\n".join(f"  - {p}" for p in problems)
                        bot.send_message(ADMIN_ID, alert)
                    except:
                        pass

            # Web research scan: elke dag om 03:00 UTC (stil, geen notificatie tenzij problemen)
            if hour == 3 and last_research != str(now.date()):
                try:
                    log("Starting daily web research scan...")
                    findings = web_research_scan()
                    last_research = str(now.date())
                    log(f"Research scan done: {len(findings)} findings")

                    # Alleen notificeren als er affiliate link problemen zijn
                    research = load_research()
                    broken = [i for i in research.get("seo_insights", [])[-6:]
                              if "⚠️" in i.get("insight", "")]
                    if broken:
                        alert = "🔬 Research Alert — Affiliate Link Problemen:\n"
                        alert += "\n".join(f"  - {b['insight']}" for b in broken)
                        bot.send_message(ADMIN_ID, alert)
                except Exception as e:
                    log(f"Research scan error: {e}")

            # Sitemap rebuild: elke dag om 02:00 UTC (na artikel generatie)
            if hour == 2 and last_research != str(now.date()) + "-sitemap":
                try:
                    count = rebuild_sitemap()
                    rebuild_robots_txt()
                    run_command(f"cd {REPO_ROOT} && git add sitemap.xml robots.txt && git commit -m 'Victor: daily sitemap rebuild ({count} URLs)' && git push origin main")
                    log(f"Daily sitemap rebuild: {count} URLs")
                except Exception as e:
                    log(f"Sitemap rebuild error: {e}")

            # Auto-improve: woensdag en zaterdag om 04:00 UTC
            if weekday in [2, 5] and hour == 4 and last_auto_improve != str(now.date()):
                try:
                    log("Starting auto-improve cycle...")
                    improved = auto_improve_articles()
                    last_auto_improve = str(now.date())
                    if improved:
                        report = f"🔄 Auto-Improve Resultaten:\n" + "\n".join(f"  - {i}" for i in improved)
                        bot.send_message(ADMIN_ID, report)
                        log(f"Auto-improved {len(improved)} articles")
                    else:
                        log("Auto-improve: no articles needed improvement")
                except Exception as e:
                    log(f"Auto-improve error: {e}")

            # Dagelijks rapport om 06:00 en 18:00 UTC
            if hour in [6, 18] and last_report != f"{now.date()}-{hour}":
                report = generate_status_report()
                problems, fixes = check_article_pipeline()
                if fixes:
                    report += "\n\n✅ Auto-fixes:\n" + "\n".join(f"  - {f}" for f in fixes)
                if problems:
                    report += "\n\n⚠️ Issues:\n" + "\n".join(f"  - {p}" for p in problems)
                else:
                    report += "\n\n✅ Pipeline gezond — alles draait"

                # Voeg brain stats toe aan avondrapport
                if hour == 18:
                    skills = load_skills()
                    long_mem = load_long_memory()
                    report += f"\n\n🧠 Brain: {len(skills.get('solutions', {}))} oplossingen, "
                    report += f"{len(long_mem.get('wins', []))} wins, "
                    report += f"{len(skills.get('avoided', []))} vermijdpatronen"

                try:
                    bot.send_message(ADMIN_ID, report)
                except:
                    pass
                last_report = f"{now.date()}-{hour}"

            # 💰 REVENUE INTELLIGENCE: dagelijks om 04:00 UTC
            if hour == 4 and last_auto_improve != str(now.date()) + "-revenue":
                try:
                    log("Revenue intelligence cycle...")
                    estimates = calculate_article_revenue()
                    roi = calculate_roi_scores()
                    build_conversion_funnels()
                    # Update dashboard
                    dashboard_html = generate_admin_dashboard()
                    dashboard_dir = f"{REPO_ROOT}/admin"
                    os.makedirs(dashboard_dir, exist_ok=True)
                    with open(f"{dashboard_dir}/index.html", 'w', encoding='utf-8') as f:
                        f.write(dashboard_html)
                    run_command(f"cd {REPO_ROOT} && git add admin/ && git diff --cached --quiet || git commit -m 'Victor: dashboard update' && git push origin main")
                    log(f"Revenue cycle done: {len(estimates)} articles tracked")
                except Exception as e:
                    log(f"Revenue cycle error: {e}")

            # 🕵️ COMPETITOR DOMINATION: dagelijkse cyclus om 04:30 UTC
            if hour == 4 and last_auto_improve != str(now.date()) + "-competitor":
                try:
                    log("Starting competitor domination cycle...")
                    comp_actions = autonomous_competitor_cycle()
                    if comp_actions:
                        comp_report = "🕵️ Competitor Domination — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        comp_report += "\n".join(f"  ✅ {a}" for a in comp_actions)
                        # Alleen melden als er iets interessants is (niet routine scans)
                        interesting = [a for a in comp_actions if any(w in a for w in ['🏆', '📈', '📉', '🔥', 'geschreven'])]
                        if interesting:
                            bot.send_message(ADMIN_ID, comp_report)
                        log(f"Competitor cycle done: {len(comp_actions)} actions")
                except Exception as e:
                    log(f"Competitor cycle error: {e}")

            # 🚀 GROWTH ENGINE: dagelijkse cyclus om 05:00 UTC
            if hour == 5 and last_auto_improve != str(now.date()) + "-growth":
                try:
                    log("Starting autonomous growth cycle...")
                    actions = autonomous_growth_cycle()
                    if actions:
                        growth_report = "🚀 Growth Engine — Dagelijkse Cyclus\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        growth_report += "\n".join(f"  ✅ {a}" for a in actions)
                        bot.send_message(ADMIN_ID, growth_report)
                        log(f"Growth cycle done: {len(actions)} actions")
                except Exception as e:
                    log(f"Growth cycle error: {e}")

            # 🤖 AUTOPILOT ENGINE: dagelijkse cyclus om 06:30 UTC
            if hour == 6 and now.minute >= 30 and last_auto_improve != str(now.date()) + "-autopilot":
                try:
                    log("Starting autopilot cycle...")
                    ap_actions = autopilot_cycle()
                    last_auto_improve = str(now.date()) + "-autopilot"  # Prevent re-run
                    if ap_actions:
                        ap_report = "🤖 Autopilot Engine — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        ap_report += "\n".join(f"  ✅ {a}" for a in ap_actions)
                        bot.send_message(ADMIN_ID, ap_report)
                        log(f"Autopilot cycle done: {len(ap_actions)} actions")
                except Exception as e:
                    log(f"Autopilot cycle error: {e}")

            # 🔥 DOMINATION MATRIX: dagelijkse cyclus om 07:00 UTC
            if hour == 7 and weekday != 0 and last_auto_improve != str(now.date()) + "-domination":
                try:
                    log("Starting domination matrix cycle...")
                    dom_actions = domination_matrix_cycle()
                    last_auto_improve = str(now.date()) + "-domination"
                    if dom_actions:
                        dom_report = "🔥 Domination Matrix — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        dom_report += "\n".join(f"  ✅ {a}" for a in dom_actions)
                        # Alleen melden als er interessante acties zijn
                        interesting = [a for a in dom_actions if any(w in a for w in ['📈', '📉', '🏆', '🏷️', '🔗', '🏭', '📢'])]
                        if interesting:
                            bot.send_message(ADMIN_ID, dom_report)
                        log(f"Domination matrix done: {len(dom_actions)} actions")
                except Exception as e:
                    log(f"Domination matrix error: {e}")

            # ☀️ DAILY BRIEFING: elke dag om 08:00 UTC
            if hour == 8 and weekday != 0 and last_auto_improve != str(now.date()) + "-briefing":
                try:
                    log("Generating daily briefing...")
                    briefing = generate_daily_briefing()
                    bot.send_message(ADMIN_ID, briefing)
                    last_auto_improve = str(now.date()) + "-briefing"
                    log("Daily briefing sent")
                except Exception as e:
                    log(f"Daily briefing error: {e}")

            # 📋 WEEKLY SPRINT PLANNING: maandag 07:00 UTC
            if weekday == 0 and hour == 7 and last_weekly != str(now.date()) + "-sprint":
                try:
                    log("Planning weekly sprint...")
                    plan_weekly_sprint()
                    sprint = load_sprint()
                    planned = sprint.get("planned_tasks", [])
                    sprint_msg = f"📋 Sprint {sprint['current_week']} — Gepland!\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    sprint_msg += f"📌 {len(planned)} taken gepland:\n"
                    for i, t in enumerate(planned[:7], 1):
                        sprint_msg += f"  {i}. [{t['type']}] {t['target'][:40]} (prio: {t['priority']})\n"
                    bot.send_message(ADMIN_ID, sprint_msg)
                    last_weekly = str(now.date()) + "-sprint"
                    log(f"Sprint planned: {len(planned)} tasks")
                except Exception as e:
                    log(f"Sprint planning error: {e}")

            # Wekelijks strategierapport: maandag 08:00 UTC
            if weekday == 0 and hour == 8 and last_weekly != str(now.date()):
                try:
                    strategy = generate_weekly_strategy()
                    diagnose = self_diagnose()
                    growth = generate_growth_report()
                    bot.send_message(ADMIN_ID, f"📈 Wekelijks Strategie + Growth Rapport\n━━━━━━━━━━━━━━━━━━━━━\n\n{strategy}\n\n{diagnose}")
                    # Growth rapport apart (kan lang zijn)
                    bot.send_message(ADMIN_ID, growth)
                    last_weekly = str(now.date())
                except:
                    pass

            time.sleep(300)
        except Exception as e:
            log(f"Proactive loop error: {e}")
            time.sleep(60)

# ── STARTUP ─────────────────────────────────────────────────────────────────
def send_startup_message():
    try:
        report = generate_status_report()

        # Check for interrupted tasks
        interrupted = check_interrupted_tasks()
        resume_text = ""
        if interrupted:
            resumed = resume_interrupted_tasks()
            if resumed:
                resume_text = "\n\n🔄 Hervatte taken na restart:\n" + "\n".join(f"  - {r}" for r in resumed)

        bot.send_message(ADMIN_ID,
            f"🚀 Victor 11.0 Domination Matrix online!\n\n{report}"
            f"\n\n🔥 Domination: /domination /programmatic /schema /serp"
            f"\n🤖 Autopilot: /autopilot /predict /sprint /briefing"
            f"\n🧠 Self-learning: /brain /diagnose /research"
            f"\n📈 SEO: /gsc /keywords /sitemap /ogimages"
            f"\n🏗️ Code: /multifile /write /fix"
            f"\n📊 /seo /revenue /strategy /autofix"
            f"{resume_text}")
        log("Startup message sent")
    except Exception as e:
        log(f"Startup error: {e}")

# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log(f"Victor 11.0 Domination Matrix gestart — Model: {MODEL}")

    # Reset Telegram polling state — voorkomt 409 conflicts
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except Exception as e:
        log(f"Webhook reset: {e}")

    send_startup_message()

    # Start proactieve monitoring in achtergrond
    t = threading.Thread(target=proactive_loop, daemon=True)
    t.start()

    bot.infinity_polling(timeout=30, long_polling_timeout=20)
