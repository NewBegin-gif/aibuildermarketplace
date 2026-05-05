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
Victor 17.0 Omega — Powered by Claude AI<br>
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


# ── MODULE 11: NEURAL COMMAND CENTER ────────────────────────────────────────
AUDIT_FILE = "/root/felix_hq/victor_audit.json"
TRENDS_FILE = "/root/felix_hq/victor_trends.json"
TRANSLATIONS_FILE = "/root/felix_hq/victor_translations.json"
HEALING_FILE = "/root/felix_hq/victor_healing.json"

def load_audit():
    if os.path.exists(AUDIT_FILE):
        try:
            return json.load(open(AUDIT_FILE))
        except:
            pass
    return {"audits": [], "issues": [], "fixes": [], "scores": {}}

def save_audit(data):
    data["audits"] = data.get("audits", [])[-30:]
    data["issues"] = data.get("issues", [])[-200:]
    data["fixes"] = data.get("fixes", [])[-100:]
    with open(AUDIT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_trends():
    if os.path.exists(TRENDS_FILE):
        try:
            return json.load(open(TRENDS_FILE))
        except:
            pass
    return {"detected": [], "articles_written": [], "sources": [], "last_scan": None}

def save_trends(data):
    data["detected"] = data.get("detected", [])[-100:]
    data["articles_written"] = data.get("articles_written", [])[-50:]
    with open(TRENDS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_translations():
    if os.path.exists(TRANSLATIONS_FILE):
        try:
            return json.load(open(TRANSLATIONS_FILE))
        except:
            pass
    return {"translated": [], "stats": {}, "hreflang_added": []}

def save_translations(data):
    data["translated"] = data.get("translated", [])[-200:]
    with open(TRANSLATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_healing():
    if os.path.exists(HEALING_FILE):
        try:
            return json.load(open(HEALING_FILE))
        except:
            pass
    return {"incidents": [], "auto_fixes": [], "uptime_checks": [], "stats": {"total_fixes": 0, "total_incidents": 0}}

def save_healing(data):
    data["incidents"] = data.get("incidents", [])[-100:]
    data["auto_fixes"] = data.get("auto_fixes", [])[-100:]
    data["uptime_checks"] = data.get("uptime_checks", [])[-48:]
    with open(HEALING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ── 11A: TECHNICAL SEO AUDITOR ───────────────────────────────────────────

def audit_page_technical(filepath):
    """Technische SEO audit van een enkele pagina."""
    issues = []
    slug = os.path.basename(filepath).replace('.html', '')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [{"type": "error", "issue": f"Kan {slug} niet lezen: {e}", "severity": "critical"}]

    file_size = len(content.encode('utf-8'))

    # 1. Title tag check
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if not title_match:
        issues.append({"type": "missing_title", "issue": f"{slug}: Geen <title> tag", "severity": "critical", "auto_fixable": True})
    elif len(title_match.group(1)) > 60:
        issues.append({"type": "title_long", "issue": f"{slug}: Title te lang ({len(title_match.group(1))} chars, max 60)", "severity": "medium", "auto_fixable": True})
    elif len(title_match.group(1)) < 20:
        issues.append({"type": "title_short", "issue": f"{slug}: Title te kort ({len(title_match.group(1))} chars)", "severity": "medium", "auto_fixable": True})

    # 2. Meta description check
    meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    if not meta_desc:
        issues.append({"type": "missing_meta_desc", "issue": f"{slug}: Geen meta description", "severity": "high", "auto_fixable": True})
    elif len(meta_desc.group(1)) > 160:
        issues.append({"type": "meta_desc_long", "issue": f"{slug}: Meta description te lang ({len(meta_desc.group(1))} chars)", "severity": "low", "auto_fixable": True})

    # 3. H1 check
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if not h1_matches:
        issues.append({"type": "missing_h1", "issue": f"{slug}: Geen H1 tag", "severity": "high", "auto_fixable": False})
    elif len(h1_matches) > 1:
        issues.append({"type": "multiple_h1", "issue": f"{slug}: {len(h1_matches)} H1 tags (moet 1 zijn)", "severity": "medium", "auto_fixable": False})

    # 4. Image alt tags
    imgs = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
    imgs_no_alt = [i for i in imgs if 'alt=' not in i.lower() or 'alt=""' in i.lower()]
    if imgs_no_alt:
        issues.append({"type": "missing_alt", "issue": f"{slug}: {len(imgs_no_alt)}/{len(imgs)} images zonder alt tag", "severity": "medium", "auto_fixable": True})

    # 5. File size check (groot = traag)
    if file_size > 100000:  # >100KB
        issues.append({"type": "large_file", "issue": f"{slug}: Bestand te groot ({file_size//1024}KB)", "severity": "medium", "auto_fixable": False})

    # 6. Mobile viewport check
    if '<meta name="viewport"' not in content and "<meta name='viewport'" not in content:
        issues.append({"type": "no_viewport", "issue": f"{slug}: Geen viewport meta tag (slecht voor mobiel)", "severity": "high", "auto_fixable": True})

    # 7. Canonical URL check
    if 'rel="canonical"' not in content and "rel='canonical'" not in content:
        issues.append({"type": "no_canonical", "issue": f"{slug}: Geen canonical URL", "severity": "medium", "auto_fixable": True})

    # 8. Open Graph tags
    if 'og:title' not in content:
        issues.append({"type": "no_og", "issue": f"{slug}: Geen Open Graph tags", "severity": "low", "auto_fixable": True})

    # 9. Broken internal links
    internal_links = re.findall(r'href="\.?/?([^"]*?\.html)"', content)
    b2b_path = os.path.dirname(filepath)
    for link in internal_links:
        link_file = os.path.join(b2b_path, os.path.basename(link))
        if not os.path.exists(link_file):
            issues.append({"type": "broken_link", "issue": f"{slug}: Broken link naar {link}", "severity": "high", "auto_fixable": True})

    # 10. HTTPS check op externe links
    http_links = re.findall(r'href="(http://[^"]+)"', content)
    if http_links:
        issues.append({"type": "http_links", "issue": f"{slug}: {len(http_links)} onveilige HTTP links", "severity": "medium", "auto_fixable": True})

    return issues


def auto_fix_technical_issues(issues, filepath):
    """Automatisch technische SEO problemen fixen."""
    if not issues:
        return []

    fixable = [i for i in issues if i.get("auto_fixable")]
    if not fixable:
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []

    slug = os.path.basename(filepath).replace('.html', '')
    title_text = slug.replace('-', ' ').title()
    fixed = []

    for issue in fixable:
        itype = issue["type"]

        if itype == "no_viewport":
            viewport_tag = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            if '<head>' in content:
                content = content.replace('<head>', f'<head>\n{viewport_tag}')
            elif '<html' in content:
                content = content.replace('<html', f'{viewport_tag}\n<html')
            else:
                content = viewport_tag + '\n' + content
            fixed.append(f"{slug}: viewport tag toegevoegd")

        elif itype == "no_canonical":
            canonical = f'<link rel="canonical" href="https://aibuildermarketplace.com/b2b/{slug}.html">'
            if '</head>' in content:
                content = content.replace('</head>', f'{canonical}\n</head>')
            else:
                content = canonical + '\n' + content
            fixed.append(f"{slug}: canonical URL toegevoegd")

        elif itype == "missing_meta_desc":
            # Genereer meta description van content
            text_only = re.sub(r'<[^>]+>', '', content)
            text_only = re.sub(r'\s+', ' ', text_only).strip()
            desc = text_only[:155].rsplit(' ', 1)[0] + "..."
            desc = desc.replace('"', "'")
            meta_tag = f'<meta name="description" content="{desc}">'
            if '</head>' in content:
                content = content.replace('</head>', f'{meta_tag}\n</head>')
            elif '<head>' in content:
                content = content.replace('<head>', f'<head>\n{meta_tag}')
            else:
                content = meta_tag + '\n' + content
            fixed.append(f"{slug}: meta description toegevoegd")

        elif itype == "missing_title":
            title_tag = f'<title>{title_text} — AI Builder Marketplace</title>'
            if '<head>' in content:
                content = content.replace('<head>', f'<head>\n{title_tag}')
            else:
                content = title_tag + '\n' + content
            fixed.append(f"{slug}: title tag toegevoegd")

        elif itype == "title_long":
            # Verkort title
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                old_title = title_match.group(1)
                new_title = old_title[:57] + "..."
                content = content.replace(f'<title>{old_title}</title>', f'<title>{new_title}</title>')
                fixed.append(f"{slug}: title verkort")

        elif itype == "no_og":
            og_tags = f'''<meta property="og:title" content="{title_text}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://aibuildermarketplace.com/b2b/{slug}.html">
<meta property="og:site_name" content="AI Builder Marketplace">'''
            if '</head>' in content:
                content = content.replace('</head>', f'{og_tags}\n</head>')
            fixed.append(f"{slug}: Open Graph tags toegevoegd")

        elif itype == "missing_alt":
            # Voeg alt tags toe aan images zonder alt
            def add_alt(match):
                img_tag = match.group(0)
                if 'alt=' not in img_tag.lower() or 'alt=""' in img_tag.lower():
                    # Probeer src te gebruiken voor alt text
                    src_match = re.search(r'src="([^"]*)"', img_tag)
                    alt_text = title_text if not src_match else os.path.basename(src_match.group(1)).replace('-', ' ').replace('.', ' ').rsplit(' ', 1)[0]
                    if 'alt=""' in img_tag:
                        return img_tag.replace('alt=""', f'alt="{alt_text}"')
                    else:
                        return img_tag.replace('<img', f'<img alt="{alt_text}"')
                return img_tag
            content = re.sub(r'<img[^>]*>', add_alt, content, flags=re.IGNORECASE)
            fixed.append(f"{slug}: alt tags toegevoegd")

        elif itype == "http_links":
            # Upgrade HTTP naar HTTPS
            content = re.sub(r'href="http://', 'href="https://', content)
            fixed.append(f"{slug}: HTTP links geupgraded naar HTTPS")

        elif itype == "broken_link":
            # Verwijder broken links (vervang met tekst)
            broken_href = issue["issue"].split("naar ")[-1] if "naar " in issue["issue"] else ""
            if broken_href:
                content = re.sub(
                    rf'<a[^>]*href="[^"]*{re.escape(os.path.basename(broken_href))}"[^>]*>(.*?)</a>',
                    r'\1', content, flags=re.IGNORECASE
                )
                fixed.append(f"{slug}: broken link verwijderd")

    if fixed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return fixed


def full_site_audit():
    """Voer een volledige technische SEO audit uit op alle pagina's."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return {"total_pages": 0, "issues": [], "score": 0}

    files = [f for f in os.listdir(b2b_path) if f.endswith('.html')]
    all_issues = []
    all_fixes = []

    for f in files:
        filepath = os.path.join(b2b_path, f)
        issues = audit_page_technical(filepath)
        if issues:
            all_issues.extend(issues)
            # Auto-fix wat kan
            fixes = auto_fix_technical_issues(issues, filepath)
            all_fixes.extend(fixes)

    # Also audit index.html and b2b.html
    for root_file in ['index.html', 'b2b.html']:
        root_path = f"{REPO_ROOT}/{root_file}"
        if os.path.exists(root_path):
            issues = audit_page_technical(root_path)
            if issues:
                all_issues.extend(issues)
                fixes = auto_fix_technical_issues(issues, root_path)
                all_fixes.extend(fixes)

    # Calculate health score
    total_pages = len(files) + 2  # +index +b2b
    critical = sum(1 for i in all_issues if i.get("severity") == "critical")
    high = sum(1 for i in all_issues if i.get("severity") == "high")
    medium = sum(1 for i in all_issues if i.get("severity") == "medium")
    low = sum(1 for i in all_issues if i.get("severity") == "low")

    # Score: start at 100, deduct per issue
    score = max(0, 100 - (critical * 15) - (high * 8) - (medium * 3) - (low * 1))

    # Git push fixes
    if all_fixes:
        try:
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: auto-fixed {len(all_fixes)} technical SEO issues' && git push origin main")
        except:
            pass

    # Save audit results
    audit = load_audit()
    audit["audits"].append({
        "date": str(datetime.now()),
        "total_pages": total_pages,
        "issues_found": len(all_issues),
        "auto_fixed": len(all_fixes),
        "score": score
    })
    audit["issues"] = all_issues
    audit["fixes"].extend([{"fix": f, "date": str(datetime.now().date())} for f in all_fixes])
    audit["scores"][str(datetime.now().date())] = score
    save_audit(audit)

    return {
        "total_pages": total_pages,
        "issues": all_issues,
        "fixes": all_fixes,
        "score": score,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }


# ── 11B: TREND RADAR ────────────────────────────────────────────────────

AI_TREND_KEYWORDS = [
    "AI tool launch", "new AI startup", "AI acquisition",
    "ChatGPT update", "Claude update", "Gemini update",
    "AI video generator", "AI voice clone", "AI website builder",
    "AI coding tool", "text to video AI", "AI image generator 2026",
    "best AI tools", "AI productivity", "AI for business",
    "synthesia alternative", "invideo alternative", "replit alternative",
    "kinsta vs", "murf ai", "bitvavo crypto",
    "AI automation", "no-code AI", "AI SaaS tools"
]


def scan_trending_topics():
    """Scan het web voor trending AI topics."""
    trends = load_trends()
    detected = []

    for keyword in AI_TREND_KEYWORDS[:8]:  # Max 8 per scan (rate limiting)
        try:
            # Gebruik een simpele web search via urllib
            search_url = f"https://www.google.com/search?q={urllib.request.quote(keyword)}&tbs=qdr:w"  # Laatste week
            req = urllib.request.Request(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; VictorBot/12.0)'
            })

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                # Extract titels uit zoekresultaten
                titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
                titles = [re.sub(r'<[^>]+>', '', t) for t in titles[:5]]

                if titles:
                    detected.append({
                        "keyword": keyword,
                        "results": titles[:3],
                        "date": str(datetime.now().date())
                    })
            except:
                pass

            time.sleep(2)  # Rate limiting
        except Exception as e:
            log(f"Trend scan error for {keyword}: {e}")

    # Analyseer trends met Claude
    if detected:
        try:
            trend_summary = "\n".join([
                f"Keyword: {d['keyword']}\nResults: {', '.join(d['results'][:2])}"
                for d in detected[:5]
            ])

            res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": """Je bent een AI trend analist. Analyseer deze zoekresultaten en identificeer:
1. Hot trending topics (nieuwe tools, updates, verschuivingen)
2. Content kansen (artikelen die we SNEL moeten schrijven)
3. Seizoensgebonden patronen

Antwoord in JSON:
{"hot_topics": [{"topic": "...", "urgency": "high/medium/low", "article_idea": "..."}], "opportunities": ["..."], "patterns": ["..."]}"""
                    },
                    {"role": "user", "content": trend_summary}
                ],
                max_tokens=1500,
                temperature=0.5
            )
            analysis = res.choices[0].message.content.strip()
            if "```json" in analysis:
                analysis = analysis.split("```json")[1].split("```")[0]
            elif "```" in analysis:
                analysis = analysis.split("```")[1].split("```")[0]
            trend_data = json.loads(analysis)

            # Save
            trends["detected"].extend(detected)
            trends["last_scan"] = str(datetime.now())
            if "hot_topics" in trend_data:
                for topic in trend_data["hot_topics"]:
                    topic["detected_date"] = str(datetime.now().date())
                trends["detected"].extend([{
                    "keyword": t.get("topic", ""),
                    "urgency": t.get("urgency", "medium"),
                    "article_idea": t.get("article_idea", ""),
                    "date": str(datetime.now().date()),
                    "source": "ai_analysis"
                } for t in trend_data.get("hot_topics", [])])

            save_trends(trends)
            return trend_data

        except Exception as e:
            log(f"Trend analysis error: {e}")
            trends["detected"].extend(detected)
            save_trends(trends)

    return {"hot_topics": [], "opportunities": [], "patterns": []}


def auto_write_trend_article():
    """Schrijf automatisch een artikel over een trending topic."""
    trends = load_trends()
    hot = [t for t in trends.get("detected", [])
           if t.get("urgency") == "high" and t.get("article_idea")
           and t.get("source") == "ai_analysis"]

    # Filter al geschreven
    written_topics = {a.get("topic", "") for a in trends.get("articles_written", [])}
    new_hot = [t for t in hot if t.get("article_idea", "") not in written_topics]

    if not new_hot:
        return None

    topic = new_hot[0]
    article_idea = topic.get("article_idea", topic.get("keyword", "AI trend"))

    try:
        # Genereer slug
        slug = re.sub(r'[^a-z0-9-]', '', article_idea.lower().replace(' ', '-'))[:60]

        # Check of het al bestaat
        target = f"{REPO_ROOT}/b2b/{slug}.html"
        if os.path.exists(target):
            return None

        # Zoek relevante affiliate links
        aff_info = "\n".join([f"{b}: {url}" for b, url in VAULT.items()])

        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Je bent een SEO content expert voor AI Builder Marketplace. Schrijf complete HTML artikelen met dark theme styling (donkere achtergrond, lichte tekst). Gebruik professionele, informatieve toon."},
                {"role": "user", "content": f"""Schrijf een trending artikel over: {article_idea}

Dit is een HOT topic nu. Focus op:
- Wat is er nieuw/veranderd
- Waarom dit belangrijk is
- Praktische tips voor gebruikers
- Vergelijking met alternatieven

Beschikbare affiliate links (gebruik waar relevant):
{aff_info}

2000-3000 woorden, complete HTML met dark theme, SEO geoptimaliseerd."""}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        html_content = res.choices[0].message.content.strip()

        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()

        os.makedirs(f"{REPO_ROOT}/b2b", exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Schema markup toevoegen
        add_schema_to_article(target)

        trends["articles_written"].append({
            "topic": article_idea,
            "slug": slug,
            "date": str(datetime.now().date()),
            "urgency": topic.get("urgency", "high")
        })
        save_trends(trends)

        # Git push
        rebuild_sitemap()
        run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: trending article — {slug}' && git push origin main")

        return slug
    except Exception as e:
        log(f"Trend article error: {e}")
        return None


# ── 11C: MULTI-LANGUAGE EXPANSION ────────────────────────────────────────

def translate_article_to_english(slug):
    """Vertaal een Nederlands artikel naar Engels met SEO-optimalisatie."""
    nl_path = f"{REPO_ROOT}/b2b/{slug}.html"
    en_dir = f"{REPO_ROOT}/en"
    en_path = f"{en_dir}/{slug}.html"

    if not os.path.exists(nl_path):
        return None
    if os.path.exists(en_path):
        return None  # Al vertaald

    try:
        with open(nl_path, 'r', encoding='utf-8') as f:
            nl_content = f.read()

        # Vertaal via Claude
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": """Je bent een professionele vertaler en SEO expert. Vertaal dit Nederlandse HTML artikel naar Engels.

Regels:
- Behoud EXACT dezelfde HTML structuur en styling
- Vertaal alle tekst naar vloeiend, native Engels
- Optimaliseer de title en meta description voor Engelse SEO
- Behoud alle links, images, en affiliate URLs ongewijzigd
- Voeg hreflang tags toe in de <head>:
  <link rel="alternate" hreflang="nl" href="https://aibuildermarketplace.com/b2b/{slug}.html">
  <link rel="alternate" hreflang="en" href="https://aibuildermarketplace.com/en/{slug}.html">
- Vertaal NIET: brand namen, URLs, code snippets"""},
                {"role": "user", "content": nl_content[:6000]}
            ],
            max_tokens=4000,
            temperature=0.3
        )
        en_content = res.choices[0].message.content.strip()

        if "```html" in en_content:
            en_content = en_content.split("```html")[1].split("```")[0].strip()
        elif "```" in en_content:
            en_content = en_content.split("```")[1].split("```")[0].strip()

        # Ensure hreflang is present
        if 'hreflang' not in en_content:
            hreflang = f'<link rel="alternate" hreflang="nl" href="https://aibuildermarketplace.com/b2b/{slug}.html">\n'
            hreflang += f'<link rel="alternate" hreflang="en" href="https://aibuildermarketplace.com/en/{slug}.html">'
            if '</head>' in en_content:
                en_content = en_content.replace('</head>', f'{hreflang}\n</head>')

        os.makedirs(en_dir, exist_ok=True)
        with open(en_path, 'w', encoding='utf-8') as f:
            f.write(en_content)

        # Voeg ook hreflang toe aan het NL artikel
        if 'hreflang' not in nl_content:
            hreflang_nl = f'<link rel="alternate" hreflang="nl" href="https://aibuildermarketplace.com/b2b/{slug}.html">\n'
            hreflang_nl += f'<link rel="alternate" hreflang="en" href="https://aibuildermarketplace.com/en/{slug}.html">'
            if '</head>' in nl_content:
                nl_content = nl_content.replace('</head>', f'{hreflang_nl}\n</head>')
                with open(nl_path, 'w', encoding='utf-8') as f:
                    f.write(nl_content)

        # Track
        trans = load_translations()
        trans["translated"].append({
            "slug": slug,
            "date": str(datetime.now().date()),
            "nl_path": f"b2b/{slug}.html",
            "en_path": f"en/{slug}.html"
        })
        trans["hreflang_added"].append(slug)
        trans["stats"]["total"] = len(trans["translated"])
        save_translations(trans)

        return slug
    except Exception as e:
        log(f"Translation error for {slug}: {e}")
        return None


def translation_batch(max_articles=2):
    """Vertaal een batch artikelen naar Engels — prioriteit op high-revenue."""
    b2b_path = f"{REPO_ROOT}/b2b"
    en_path = f"{REPO_ROOT}/en"

    if not os.path.isdir(b2b_path):
        return []

    files = [f.replace('.html', '') for f in os.listdir(b2b_path) if f.endswith('.html')]
    already = set()
    if os.path.isdir(en_path):
        already = {f.replace('.html', '') for f in os.listdir(en_path) if f.endswith('.html')}

    to_translate = [s for s in files if s not in already]

    # Prioriteer op affiliate content (money pages eerst)
    def priority_score(slug):
        score = 0
        for brand in VAULT:
            if brand.lower() in slug:
                score += 10
        if 'vs' in slug:
            score += 5
        if 'review' in slug:
            score += 4
        if 'pricing' in slug or 'alternative' in slug:
            score += 3
        return score

    to_translate.sort(key=priority_score, reverse=True)

    translated = []
    for slug in to_translate[:max_articles]:
        result = translate_article_to_english(slug)
        if result:
            translated.append(result)
            time.sleep(2)

    if translated:
        try:
            rebuild_sitemap()
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: {len(translated)} EN translations + hreflang' && git push origin main")
        except:
            pass

    return translated


# ── 11D: INTERACTIVE TELEGRAM PANELS ─────────────────────────────────────

def build_inline_keyboard(buttons):
    """Bouw een Telegram InlineKeyboardMarkup."""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for row in buttons:
        btn_row = []
        for text, callback_data in row:
            btn_row.append(telebot.types.InlineKeyboardButton(text, callback_data=callback_data))
        markup.row(*btn_row)
    return markup


def build_main_dashboard_keyboard():
    """Hoofdmenu inline keyboard."""
    return build_inline_keyboard([
        [("📊 Status", "dash_status"), ("📈 SERP", "dash_serp")],
        [("💰 Revenue", "dash_revenue"), ("🕵️ Competitors", "dash_competitors")],
        [("🤖 Autopilot", "dash_autopilot"), ("🔥 Domination", "dash_domination")],
        [("🏷️ Schema", "dash_schema"), ("🔗 Links", "dash_links")],
        [("🧠 Brain", "dash_brain"), ("☀️ Briefing", "dash_briefing")],
        [("🔧 Audit", "dash_audit"), ("🌍 Translate", "dash_translate")],
        [("📊 Scorecard", "dash_scorecard"), ("🏆 Leaderboard", "dash_leaderboard")],
        [("🧬 DNA", "dash_dna"), ("🔗 Backlinks", "dash_backlinks")],
        [("📅 Calendar", "dash_calendar"), ("🏛️ Palace", "dash_palace")],
        [("📧 Outreach", "dash_outreach"), ("🛰️ Skynet", "dash_skynet")],
        [("💰 Revenue2", "dash_revenue2"), ("🏛️ Authority", "dash_authority")],
        [("🔮 Predict", "dash_predict"), ("🔮 Quantum", "dash_quantum")],
        [("💉 Monetize", "dash_monetize"), ("🏰 E-E-A-T", "dash_eeat")],
        [("⚔️ War Room", "dash_warroom"), ("🌀 Omega", "dash_omega")]
    ])


def build_action_keyboard():
    """Snelle acties keyboard."""
    return build_inline_keyboard([
        [("📝 Genereer Artikel", "act_generate"), ("🏭 Programmatic", "act_programmatic")],
        [("🔄 Improve", "act_improve"), ("🎯 Sprint Run", "act_sprint")],
        [("🔥 Full Domination", "act_domination"), ("📋 Help", "act_help")]
    ])


# ── 11E: SELF-HEALING SYSTEM ────────────────────────────────────────────

def self_healing_check():
    """Volledige self-healing check: detecteer en fix problemen automatisch."""
    healing = load_healing()
    incidents = []
    auto_fixes = []

    # 1. Website uptime check
    try:
        req = urllib.request.Request(
            "https://aibuildermarketplace.com",
            headers={'User-Agent': 'VictorBot/12.0 HealthCheck'}
        )
        start = time.time()
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            response_time = time.time() - start
            healing["uptime_checks"].append({
                "time": str(datetime.now()),
                "status": status,
                "response_time": round(response_time, 2)
            })

            if response_time > 5:
                incidents.append({
                    "type": "slow_response",
                    "detail": f"Site is traag: {response_time:.1f}s",
                    "severity": "medium",
                    "time": str(datetime.now())
                })

            if status != 200:
                incidents.append({
                    "type": "http_error",
                    "detail": f"Site returned {status}",
                    "severity": "critical",
                    "time": str(datetime.now())
                })
    except Exception as e:
        incidents.append({
            "type": "site_down",
            "detail": f"Site niet bereikbaar: {e}",
            "severity": "critical",
            "time": str(datetime.now())
        })

    # 2. Git repo health check
    git_status = run_command(f"cd {REPO_ROOT} && git status --porcelain")
    if "HEAD detached" in git_status:
        # Auto-fix: checkout main
        run_command(f"cd {REPO_ROOT} && git checkout main")
        auto_fixes.append("Git HEAD was detached — checkout main")

    # 3. Check for .lock files
    lock_file = f"{REPO_ROOT}/.git/HEAD.lock"
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            auto_fixes.append("Stale git HEAD.lock verwijderd")
        except:
            pass

    index_lock = f"{REPO_ROOT}/.git/index.lock"
    if os.path.exists(index_lock):
        try:
            os.remove(index_lock)
            auto_fixes.append("Stale git index.lock verwijderd")
        except:
            pass

    # 4. Check disk space
    disk_check = run_command("df -h /root | tail -1")
    if disk_check:
        parts = disk_check.split()
        if len(parts) >= 5:
            use_pct = parts[4].replace('%', '')
            try:
                if int(use_pct) > 90:
                    incidents.append({
                        "type": "disk_full",
                        "detail": f"Disk {use_pct}% vol!",
                        "severity": "critical",
                        "time": str(datetime.now())
                    })
                    # Auto-fix: cleanup logs
                    run_command("find /root/felix_hq -name '*.log' -size +10M -exec truncate -s 1M {} \\;")
                    auto_fixes.append("Grote log files opgeruimd")
            except:
                pass

    # 5. Check of alle HTML files valid zijn (niet leeg / corrupt)
    b2b_path = f"{REPO_ROOT}/b2b"
    if os.path.isdir(b2b_path):
        for f in os.listdir(b2b_path):
            if f.endswith('.html'):
                filepath = os.path.join(b2b_path, f)
                try:
                    size = os.path.getsize(filepath)
                    if size == 0:
                        incidents.append({
                            "type": "empty_file",
                            "detail": f"Leeg bestand: {f}",
                            "severity": "high",
                            "time": str(datetime.now())
                        })
                    elif size < 100:
                        incidents.append({
                            "type": "corrupt_file",
                            "detail": f"Waarschijnlijk corrupt: {f} ({size} bytes)",
                            "severity": "high",
                            "time": str(datetime.now())
                        })
                except:
                    pass

    # 6. Check API health (OpenRouter)
    try:
        test_res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        if not test_res.choices:
            incidents.append({
                "type": "api_error",
                "detail": "OpenRouter API returned empty response",
                "severity": "high",
                "time": str(datetime.now())
            })
    except Exception as e:
        incidents.append({
            "type": "api_error",
            "detail": f"OpenRouter API error: {str(e)[:100]}",
            "severity": "critical",
            "time": str(datetime.now())
        })

    # 7. Memory/process check
    mem_check = run_command("free -m | grep Mem")
    if mem_check:
        parts = mem_check.split()
        if len(parts) >= 4:
            try:
                total = int(parts[1])
                used = int(parts[2])
                pct = (used / total) * 100
                if pct > 90:
                    incidents.append({
                        "type": "memory_high",
                        "detail": f"RAM gebruik {pct:.0f}% ({used}MB/{total}MB)",
                        "severity": "high",
                        "time": str(datetime.now())
                    })
            except:
                pass

    # Save results
    healing["incidents"].extend(incidents)
    healing["auto_fixes"].extend([{"fix": f, "time": str(datetime.now())} for f in auto_fixes])
    healing["stats"]["total_fixes"] = healing["stats"].get("total_fixes", 0) + len(auto_fixes)
    healing["stats"]["total_incidents"] = healing["stats"].get("total_incidents", 0) + len(incidents)
    save_healing(healing)

    return incidents, auto_fixes


def neural_command_cycle():
    """Volledige Neural Command Center cyclus — draait dagelijks."""
    actions = []

    # 1. Self-healing check
    try:
        incidents, fixes = self_healing_check()
        if fixes:
            actions.append(f"🔧 Self-healing: {len(fixes)} auto-fixes")
        if incidents:
            critical = [i for i in incidents if i.get("severity") == "critical"]
            if critical:
                actions.append(f"🚨 {len(critical)} kritieke problemen gedetecteerd!")
            else:
                actions.append(f"⚠️ {len(incidents)} issues gevonden")
        else:
            actions.append("✅ Systeem gezond")
    except Exception as e:
        log(f"Self-healing error: {e}")

    # 2. Technical SEO audit (1x per week op woensdag)
    if datetime.now().weekday() == 2:
        try:
            result = full_site_audit()
            actions.append(f"🔍 SEO Audit: score {result['score']}/100, {len(result.get('fixes', []))} auto-fixes")
        except Exception as e:
            log(f"Audit error: {e}")

    # 3. Trend radar scan
    try:
        trend_data = scan_trending_topics()
        hot = trend_data.get("hot_topics", [])
        if hot:
            high_urgency = [t for t in hot if t.get("urgency") == "high"]
            actions.append(f"📡 Trend Radar: {len(hot)} topics, {len(high_urgency)} urgent")

            # Auto-write trend article als er high urgency is
            if high_urgency:
                written = auto_write_trend_article()
                if written:
                    actions.append(f"🔥 Trending artikel geschreven: {written}")
    except Exception as e:
        log(f"Trend radar error: {e}")

    # 4. Translation batch (1x per week op donderdag)
    if datetime.now().weekday() == 3:
        try:
            translated = translation_batch(max_articles=2)
            if translated:
                actions.append(f"🌍 {len(translated)} artikelen vertaald naar Engels")
        except Exception as e:
            log(f"Translation error: {e}")

    return actions


# ── MODULE 12: HIVE MIND ENGINE ─────────────────────────────────────────────
CONVERSION_FILE = "/root/felix_hq/victor_conversions.json"
BACKLINKS_FILE = "/root/felix_hq/victor_backlinks.json"
DNA_FILE = "/root/felix_hq/victor_dna.json"
AB2_FILE = "/root/felix_hq/victor_ab2.json"

def load_conversions():
    if os.path.exists(CONVERSION_FILE):
        try:
            return json.load(open(CONVERSION_FILE))
        except:
            pass
    return {"articles": {}, "winning_patterns": [], "conversion_log": [], "top_performers": []}

def save_conversions(data):
    data["conversion_log"] = data.get("conversion_log", [])[-200:]
    data["winning_patterns"] = data.get("winning_patterns", [])[-50:]
    with open(CONVERSION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_backlinks():
    if os.path.exists(BACKLINKS_FILE):
        try:
            return json.load(open(BACKLINKS_FILE))
        except:
            pass
    return {"opportunities": [], "outreach_sent": [], "backlinks_found": [], "stats": {}}

def save_backlinks(data):
    data["opportunities"] = data.get("opportunities", [])[-200:]
    data["outreach_sent"] = data.get("outreach_sent", [])[-100:]
    with open(BACKLINKS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_dna():
    if os.path.exists(DNA_FILE):
        try:
            return json.load(open(DNA_FILE))
        except:
            pass
    return {"blueprint": {}, "article_scores": {}, "recommendations": [], "last_analysis": None}

def save_dna(data):
    data["recommendations"] = data.get("recommendations", [])[-50:]
    with open(DNA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_ab2():
    if os.path.exists(AB2_FILE):
        try:
            return json.load(open(AB2_FILE))
        except:
            pass
    return {"tests": [], "completed": [], "insights": []}

def save_ab2(data):
    data["completed"] = data.get("completed", [])[-50:]
    data["insights"] = data.get("insights", [])[-30:]
    with open(AB2_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ── 12A: CONVERSION INTELLIGENCE ────────────────────────────────────────

def analyze_article_conversions():
    """Analyseer welke artikelen het beste converteren op basis van GSC + affiliate data."""
    conv = load_conversions()

    # Haal GSC data op
    gsc_data = {}
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc_data = json.load(f)
        except:
            pass

    # Haal revenue data op
    rev_data = {}
    if os.path.exists(REVENUE_FILE):
        try:
            with open(REVENUE_FILE) as f:
                rev_data = json.load(f)
        except:
            pass

    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return conv

    articles = {}
    for f in os.listdir(b2b_path):
        if not f.endswith('.html'):
            continue
        slug = f.replace('.html', '')
        filepath = os.path.join(b2b_path, f)

        try:
            with open(filepath, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except:
            continue

        # Content metrics
        text = re.sub(r'<[^>]+>', '', content)
        words = text.split()
        word_count = len(words)

        # Affiliate links count
        aff_count = sum(1 for url in VAULT.values() if url in content)

        # CTA count (buttons, call-to-action links)
        cta_patterns = re.findall(r'(try|start|sign.?up|get.?started|probeer|begin|aanmelden|koop)', content, re.IGNORECASE)
        cta_count = len(cta_patterns)

        # Headings structure
        h2_count = len(re.findall(r'<h2', content, re.IGNORECASE))
        h3_count = len(re.findall(r'<h3', content, re.IGNORECASE))

        # Images
        img_count = len(re.findall(r'<img', content, re.IGNORECASE))

        # Internal links
        internal_links = len(re.findall(r'href="[^"]*\.html"', content))

        # Lists (bullet points)
        list_items = len(re.findall(r'<li', content, re.IGNORECASE))

        # Tables
        table_count = len(re.findall(r'<table', content, re.IGNORECASE))

        # GSC performance
        clicks = 0
        impressions = 0
        position = 100
        ctr = 0
        for page in gsc_data.get("pages", []):
            if slug in page.get("page", ""):
                clicks = page.get("clicks", 0)
                impressions = page.get("impressions", 0)
                position = page.get("position", 100)
                ctr = page.get("ctr", 0)
                break

        # Revenue estimate
        est_revenue = 0
        for brand, rates in COMMISSION_RATES.items():
            if brand.lower() in slug:
                est_revenue = clicks * rates.get("est_ctr", 0.02) * rates.get("per_signup", 10)
                break

        # Conversion score (composite metric)
        conv_score = 0
        conv_score += min(clicks * 2, 40)  # Max 40 pts from clicks
        conv_score += min(ctr * 500, 20)   # Max 20 pts from CTR
        conv_score += min(est_revenue, 20)  # Max 20 pts from revenue
        conv_score += 5 if aff_count >= 2 else 0  # Affiliate link bonus
        conv_score += 5 if cta_count >= 3 else 0   # CTA bonus
        conv_score += 5 if table_count >= 1 else 0  # Table bonus
        conv_score += 5 if h2_count >= 3 else 0     # Structure bonus

        articles[slug] = {
            "word_count": word_count,
            "aff_links": aff_count,
            "cta_count": cta_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "img_count": img_count,
            "internal_links": internal_links,
            "list_items": list_items,
            "table_count": table_count,
            "clicks": clicks,
            "impressions": impressions,
            "position": round(position, 1),
            "ctr": round(ctr, 4),
            "est_revenue": round(est_revenue, 2),
            "conv_score": round(conv_score, 1),
            "date": str(datetime.now().date())
        }

    conv["articles"] = articles

    # Identify top performers
    sorted_articles = sorted(articles.items(), key=lambda x: x[1]["conv_score"], reverse=True)
    conv["top_performers"] = [
        {"slug": slug, "score": data["conv_score"], "clicks": data["clicks"], "revenue": data["est_revenue"]}
        for slug, data in sorted_articles[:10]
    ]

    # Extract winning patterns
    if len(sorted_articles) >= 5:
        top5 = [data for _, data in sorted_articles[:5]]
        bottom5 = [data for _, data in sorted_articles[-5:]]

        patterns = []
        # Compare averages
        for metric in ["word_count", "aff_links", "cta_count", "h2_count", "table_count", "img_count", "list_items"]:
            top_avg = sum(a[metric] for a in top5) / 5
            bot_avg = sum(a[metric] for a in bottom5) / 5
            if top_avg > bot_avg * 1.3:
                patterns.append({
                    "metric": metric,
                    "top_avg": round(top_avg, 1),
                    "bottom_avg": round(bot_avg, 1),
                    "insight": f"Top artikelen hebben {top_avg:.0f} {metric} vs {bot_avg:.0f} bij slechtste"
                })

        conv["winning_patterns"] = patterns

    conv["conversion_log"].append({
        "date": str(datetime.now().date()),
        "total_articles": len(articles),
        "avg_score": round(sum(a["conv_score"] for a in articles.values()) / max(len(articles), 1), 1)
    })

    save_conversions(conv)
    return conv


# ── 12B: BACKLINK HUNTER ────────────────────────────────────────────────

BACKLINK_SEARCH_QUERIES = [
    "beste AI tools lijst",
    "AI tool vergelijking",
    "AI software resources",
    "top AI tools for business",
    "best AI tools list 2026",
    "AI tool comparison",
    "AI software directory",
    "AI tools roundup",
    "synthesia alternatives list",
    "kinsta alternatives list",
    "replit alternatives",
    "video AI tools resources"
]


def hunt_backlink_opportunities():
    """Zoek backlink kansen: resource pages, broken links, mentions."""
    bl = load_backlinks()
    opportunities = []
    already_found = {o.get("url", "") for o in bl.get("opportunities", [])}

    for query in BACKLINK_SEARCH_QUERIES[:4]:  # Max 4 per scan
        try:
            search_url = f"https://www.google.com/search?q={urllib.request.quote(query)}"
            req = urllib.request.Request(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; VictorBot/13.0)'
            })

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                # Extract URLs
                urls = re.findall(r'href="(https?://[^"]+)"', html)
                # Filter out Google's own URLs
                external_urls = [u for u in urls
                                if 'google.' not in u and 'gstatic' not in u
                                and 'youtube.' not in u and u not in already_found
                                and 'aibuildermarketplace' not in u][:5]

                for url in external_urls:
                    # Classify opportunity type
                    opp_type = "resource_page"
                    if 'alternative' in query or 'vs' in query:
                        opp_type = "comparison_mention"
                    elif 'list' in query or 'top' in query or 'best' in query:
                        opp_type = "listicle"

                    opportunities.append({
                        "url": url,
                        "type": opp_type,
                        "query": query,
                        "date": str(datetime.now().date()),
                        "status": "found"
                    })

            except:
                pass

            time.sleep(3)
        except Exception as e:
            log(f"Backlink hunt error for {query}: {e}")

    if opportunities:
        bl["opportunities"].extend(opportunities)
        bl["stats"]["total_found"] = len(bl["opportunities"])
        bl["stats"]["last_hunt"] = str(datetime.now().date())
        save_backlinks(bl)

    return opportunities


def generate_outreach_email(opportunity):
    """Genereer een outreach email voor een backlink kans."""
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": """Je bent een outreach specialist voor AI Builder Marketplace (aibuildermarketplace.com).
Schrijf een korte, persoonlijke outreach email in het Engels.
De email moet:
- Kort zijn (max 150 woorden)
- Waarde bieden (niet alleen om een link vragen)
- Relevant zijn voor hun content
- Professioneel maar warm
- Een specifieke pagina van ons suggereren die waarde toevoegt

Antwoord ALLEEN met de email tekst (subject + body), geen uitleg."""},
                {"role": "user", "content": f"""Genereer een outreach email voor:
URL: {opportunity['url']}
Type: {opportunity['type']}
Zoekterm: {opportunity['query']}

Onze relevante pagina's:
- https://aibuildermarketplace.com/b2b.html (AI tools overzicht)
- https://aibuildermarketplace.com (homepage)"""}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        log(f"Outreach email error: {e}")
        return None


def backlink_batch():
    """Zoek nieuwe backlink kansen en genereer outreach emails."""
    opportunities = hunt_backlink_opportunities()

    # Genereer outreach voor de beste kansen (max 2 per batch)
    bl = load_backlinks()
    new_outreach = []
    unemailed = [o for o in bl.get("opportunities", []) if o.get("status") == "found"]

    for opp in unemailed[:2]:
        email = generate_outreach_email(opp)
        if email:
            opp["status"] = "email_ready"
            opp["outreach_email"] = email
            new_outreach.append({
                "url": opp["url"],
                "email": email,
                "date": str(datetime.now().date())
            })

    if new_outreach:
        bl["outreach_sent"].extend(new_outreach)
        save_backlinks(bl)

    return len(opportunities), len(new_outreach)


# ── 12C: CONTENT DNA ANALYZER ───────────────────────────────────────────

def analyze_content_dna():
    """Analyseer de DNA van top-performende artikelen om een blueprint te maken."""
    conv = load_conversions()
    articles = conv.get("articles", {})

    if len(articles) < 5:
        # Eerst conversion analyse draaien
        conv = analyze_article_conversions()
        articles = conv.get("articles", {})

    if len(articles) < 3:
        return None

    # Sorteer op conversion score
    sorted_arts = sorted(articles.items(), key=lambda x: x[1].get("conv_score", 0), reverse=True)
    top_articles = dict(sorted_arts[:max(3, len(sorted_arts) // 4)])  # Top 25%
    all_articles = dict(sorted_arts)

    # Bereken blueprint (ideale waarden)
    blueprint = {}
    metrics = ["word_count", "aff_links", "cta_count", "h2_count", "h3_count",
               "img_count", "internal_links", "list_items", "table_count"]

    for metric in metrics:
        top_values = [a[metric] for a in top_articles.values()]
        all_values = [a[metric] for a in all_articles.values()]

        blueprint[metric] = {
            "ideal": round(sum(top_values) / len(top_values), 1),
            "average": round(sum(all_values) / len(all_values), 1),
            "min_top": min(top_values),
            "max_top": max(top_values)
        }

    # AI analyse van top content voor kwalitatieve inzichten
    top_slugs = list(top_articles.keys())[:3]
    b2b_path = f"{REPO_ROOT}/b2b"
    content_samples = []
    for slug in top_slugs:
        filepath = f"{b2b_path}/{slug}.html"
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = re.sub(r'<[^>]+>', '', f.read())
                content_samples.append(f"--- {slug} ---\n{text[:1000]}")

    qualitative = {}
    if content_samples:
        try:
            res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": """Analyseer deze top-performende artikelen en extract het "DNA" — de patronen die ze succesvol maken.
Antwoord in JSON:
{
    "tone": "beschrijving van de schrijfstijl",
    "intro_pattern": "hoe beginnen de intros",
    "cta_style": "hoe worden CTAs gepresenteerd",
    "structure_pattern": "gemeenschappelijke structuur",
    "unique_elements": ["element1", "element2"],
    "recommendations": ["tip1", "tip2", "tip3"]
}"""
                    },
                    {"role": "user", "content": "\n\n".join(content_samples)}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            result = res.choices[0].message.content.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            qualitative = json.loads(result)
        except Exception as e:
            log(f"DNA qualitative analysis error: {e}")

    # Score elk artikel tegen de blueprint
    article_scores = {}
    for slug, data in all_articles.items():
        score = 0
        total_checks = 0
        for metric in metrics:
            ideal = blueprint[metric]["ideal"]
            actual = data.get(metric, 0)
            if ideal > 0:
                ratio = min(actual / ideal, 2.0)  # Cap at 200%
                if 0.7 <= ratio <= 1.5:
                    score += 1  # Within sweet spot
                total_checks += 1
        dna_match = round((score / max(total_checks, 1)) * 100, 1)
        article_scores[slug] = dna_match

    # Save
    dna = load_dna()
    dna["blueprint"] = blueprint
    dna["blueprint"]["qualitative"] = qualitative
    dna["article_scores"] = article_scores
    dna["last_analysis"] = str(datetime.now())

    # Generate recommendations for worst DNA matches
    worst = sorted(article_scores.items(), key=lambda x: x[1])[:5]
    dna["recommendations"] = []
    for slug, match_pct in worst:
        art = all_articles.get(slug, {})
        tips = []
        for metric in metrics:
            ideal = blueprint[metric]["ideal"]
            actual = art.get(metric, 0)
            if ideal > 0 and actual < ideal * 0.5:
                tips.append(f"{metric}: {actual} → ideaal {ideal:.0f}")
        dna["recommendations"].append({
            "slug": slug,
            "dna_match": match_pct,
            "improvements": tips[:3],
            "date": str(datetime.now().date())
        })

    save_dna(dna)
    return dna


def apply_dna_to_article(slug):
    """Verbeter een artikel zodat het beter matcht met de winning DNA blueprint."""
    dna = load_dna()
    blueprint = dna.get("blueprint", {})
    if not blueprint:
        analyze_content_dna()
        dna = load_dna()
        blueprint = dna.get("blueprint", {})

    if not blueprint:
        return None

    filepath = f"{REPO_ROOT}/b2b/{slug}.html"
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build improvement prompt
    qual = blueprint.get("qualitative", {})
    prompt = f"""Verbeter dit artikel zodat het matcht met ons bewezen winnende content DNA.

Blueprint (ideale waarden):
- Woordenaantal: {blueprint.get('word_count', {}).get('ideal', 2000):.0f}
- H2 headings: {blueprint.get('h2_count', {}).get('ideal', 5):.0f}
- H3 headings: {blueprint.get('h3_count', {}).get('ideal', 3):.0f}
- Affiliate links: {blueprint.get('aff_links', {}).get('ideal', 2):.0f}
- CTAs: {blueprint.get('cta_count', {}).get('ideal', 4):.0f}
- Tabellen: {blueprint.get('table_count', {}).get('ideal', 1):.0f}
- Lijsten: {blueprint.get('list_items', {}).get('ideal', 8):.0f}
- Interne links: {blueprint.get('internal_links', {}).get('ideal', 3):.0f}
- Afbeeldingen: {blueprint.get('img_count', {}).get('ideal', 2):.0f}

Kwalitatieve stijl:
- Tone: {qual.get('tone', 'professioneel en informatief')}
- Intro: {qual.get('intro_pattern', 'kort en krachtig')}
- CTA stijl: {qual.get('cta_style', 'duidelijke buttons')}

Beschikbare affiliate links:
{chr(10).join(f'{b}: {u}' for b, u in VAULT.items())}

Behoud de bestaande content maar verbeter structuur, voeg ontbrekende elementen toe (tabellen, CTAs, headings), en match de toon.
Geef de VOLLEDIGE verbeterde HTML terug."""

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Je bent een content optimalisatie expert. Verbeter artikelen om te matchen met een bewezen winning formula. Behoud dark theme HTML styling."},
                {"role": "user", "content": f"{prompt}\n\nHuidig artikel:\n{content[:5000]}"}
            ],
            max_tokens=4000,
            temperature=0.5
        )
        improved = res.choices[0].message.content.strip()

        if "```html" in improved:
            improved = improved.split("```html")[1].split("```")[0].strip()
        elif "```" in improved:
            improved = improved.split("```")[1].split("```")[0].strip()

        if len(improved) > 500:  # Sanity check
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(improved)
            run_command(f"cd {REPO_ROOT} && git add b2b/{slug}.html && git commit -m 'Victor: DNA-optimized {slug}' && git push origin main")
            return slug
    except Exception as e:
        log(f"DNA apply error for {slug}: {e}")

    return None


# ── 12D: A/B TESTING ENGINE 2.0 ─────────────────────────────────────────

AB2_TEST_TYPES = {
    "cta_text": {
        "variants": [
            {"label": "A: Direct", "pattern": "Probeer Nu", "replacement": "Start Gratis"},
            {"label": "B: Urgency", "pattern": "Probeer Nu", "replacement": "Probeer Nu — Gratis Trial"}
        ]
    },
    "cta_color": {
        "variants": [
            {"label": "A: Purple", "style_from": "#6c63ff", "style_to": "#6c63ff"},
            {"label": "B: Green", "style_from": "#6c63ff", "style_to": "#00c853"},
            {"label": "C: Orange", "style_from": "#6c63ff", "style_to": "#ff6d00"}
        ]
    },
    "intro_style": {
        "variants": [
            {"label": "A: Question", "type": "question_intro"},
            {"label": "B: Statistic", "type": "stat_intro"}
        ]
    }
}


def create_ab2_test(slug, test_type="cta_color"):
    """Maak een nieuwe A/B test aan voor een artikel."""
    ab2 = load_ab2()

    # Check of er al een test loopt voor dit artikel
    active = [t for t in ab2["tests"] if t["slug"] == slug and t["status"] == "active"]
    if active:
        return None, "Er loopt al een test voor dit artikel"

    filepath = f"{REPO_ROOT}/b2b/{slug}.html"
    if not os.path.exists(filepath):
        return None, "Artikel niet gevonden"

    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    test = {
        "id": f"ab2_{slug}_{test_type}_{int(time.time())}",
        "slug": slug,
        "type": test_type,
        "status": "active",
        "start_date": str(datetime.now().date()),
        "current_variant": 0,
        "original_content": original_content[:100],  # Just a reference
        "variants_data": [],
        "results": {},
        "days_per_variant": 3
    }

    # Genereer varianten
    config = AB2_TEST_TYPES.get(test_type, {})
    variants = config.get("variants", [])

    if test_type == "cta_color":
        for v in variants:
            variant_content = original_content.replace(
                v["style_from"], v["style_to"]
            )
            test["variants_data"].append({
                "label": v["label"],
                "applied": False,
                "clicks": 0,
                "impressions": 0
            })
    elif test_type == "cta_text":
        for v in variants:
            test["variants_data"].append({
                "label": v["label"],
                "pattern": v["pattern"],
                "replacement": v["replacement"],
                "applied": False,
                "clicks": 0,
                "impressions": 0
            })

    # Apply first variant
    if test_type == "cta_color" and variants:
        new_content = original_content.replace(
            variants[0]["style_from"], variants[0]["style_to"]
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        test["variants_data"][0]["applied"] = True
        run_command(f"cd {REPO_ROOT} && git add b2b/{slug}.html && git commit -m 'Victor: A/B test {test_type} variant A for {slug}' && git push origin main")

    ab2["tests"].append(test)
    save_ab2(ab2)
    return test, None


def check_ab2_tests():
    """Check en roteer actieve A/B tests."""
    ab2 = load_ab2()
    actions = []

    for test in ab2["tests"]:
        if test["status"] != "active":
            continue

        start = datetime.strptime(test["start_date"], "%Y-%m-%d")
        days_active = (datetime.now() - start).days
        days_per = test.get("days_per_variant", 3)
        current_v = test.get("current_variant", 0)
        total_variants = len(test.get("variants_data", []))

        if total_variants == 0:
            continue

        # Update met GSC data
        if os.path.exists(GSC_DATA_FILE):
            try:
                with open(GSC_DATA_FILE) as f:
                    gsc = json.load(f)
                for page in gsc.get("pages", []):
                    if test["slug"] in page.get("page", ""):
                        test["variants_data"][current_v]["clicks"] = page.get("clicks", 0)
                        test["variants_data"][current_v]["impressions"] = page.get("impressions", 0)
                        break
            except:
                pass

        # Roteer naar volgende variant
        expected_v = min(days_active // days_per, total_variants - 1)
        if expected_v > current_v and expected_v < total_variants:
            test["current_variant"] = expected_v
            slug = test["slug"]
            filepath = f"{REPO_ROOT}/b2b/{slug}.html"

            if test["type"] == "cta_color" and os.path.exists(filepath):
                config = AB2_TEST_TYPES["cta_color"]
                variants = config["variants"]
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Reset naar origineel en apply nieuwe variant
                for v in variants:
                    content = content.replace(v["style_to"], variants[0]["style_from"])
                content = content.replace(variants[0]["style_from"], variants[expected_v]["style_to"])
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                run_command(f"cd {REPO_ROOT} && git add b2b/{slug}.html && git commit -m 'Victor: A/B rotating to variant {expected_v} for {slug}' && git push origin main")
                actions.append(f"🔄 A/B {slug}: variant {variants[expected_v]['label']}")

        # Check of test klaar is
        if days_active >= days_per * total_variants:
            # Bepaal winnaar
            best_v = max(range(total_variants),
                        key=lambda i: test["variants_data"][i].get("clicks", 0))
            winner = test["variants_data"][best_v]

            test["status"] = "completed"
            test["winner"] = best_v
            test["end_date"] = str(datetime.now().date())

            ab2["completed"].append({
                "slug": test["slug"],
                "type": test["type"],
                "winner": winner.get("label", f"Variant {best_v}"),
                "clicks": winner.get("clicks", 0),
                "date": str(datetime.now().date())
            })

            ab2["insights"].append({
                "insight": f"{test['slug']}: {winner.get('label', '?')} won met {winner.get('clicks', 0)} clicks",
                "date": str(datetime.now().date())
            })

            actions.append(f"🏆 A/B {test['slug']}: {winner.get('label', '?')} wint!")

    save_ab2(ab2)
    return actions


# ── 12E: TELEGRAM COMMAND CENTER (VISUAL REPORTS) ────────────────────────

def generate_ascii_bar(value, max_value, width=15):
    """Genereer een ASCII progress bar."""
    if max_value == 0:
        return "░" * width
    filled = int((value / max_value) * width)
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)


def generate_scorecard():
    """Genereer een visueel scorecard rapport."""
    # Gather all data
    conv = load_conversions()
    serp = load_serp_data()
    healing = load_healing()
    dna = load_dna()
    prog = load_programmatic()
    trans = load_translations()
    audit = load_audit()
    bl = load_backlinks()

    # Count articles
    b2b_path = f"{REPO_ROOT}/b2b"
    article_count = len([f for f in os.listdir(b2b_path) if f.endswith('.html')]) if os.path.isdir(b2b_path) else 0

    en_path = f"{REPO_ROOT}/en"
    en_count = len([f for f in os.listdir(en_path) if f.endswith('.html')]) if os.path.isdir(en_path) else 0

    # SERP stats
    tracking = serp.get("tracking", {})
    page1 = sum(1 for s, d in tracking.items() if d.get("positions") and d["positions"][-1]["pos"] <= 10)
    top3 = sum(1 for s, d in tracking.items() if d.get("positions") and d["positions"][-1]["pos"] <= 3)

    # Audit score
    audits = audit.get("audits", [])
    audit_score = audits[-1].get("score", 0) if audits else 0

    # Revenue
    total_rev = sum(a.get("est_revenue", 0) for a in conv.get("articles", {}).values())

    # DNA match average
    dna_scores = dna.get("article_scores", {})
    avg_dna = round(sum(dna_scores.values()) / max(len(dna_scores), 1), 1) if dna_scores else 0

    # Build visual report
    msg = "📊 VICTOR SCORECARD\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Content
    msg += f"📝 Content:     {article_count} artikelen\n"
    msg += f"   {generate_ascii_bar(article_count, 100)} {article_count}/100\n"
    msg += f"🌍 EN versies:  {en_count}\n"
    msg += f"   {generate_ascii_bar(en_count, article_count)} {en_count}/{article_count}\n\n"

    # Rankings
    total_tracked = len(tracking)
    msg += f"📈 Rankings:\n"
    msg += f"   Pagina 1: {generate_ascii_bar(page1, max(total_tracked,1))} {page1}/{total_tracked}\n"
    msg += f"   Top 3:    {generate_ascii_bar(top3, max(total_tracked,1))} {top3}/{total_tracked}\n\n"

    # Health
    msg += f"🏥 Site Health:\n"
    msg += f"   SEO Score:  {generate_ascii_bar(audit_score, 100)} {audit_score}/100\n"
    msg += f"   DNA Match:  {generate_ascii_bar(avg_dna, 100)} {avg_dna}%\n\n"

    # Revenue
    msg += f"💰 Revenue:     €{total_rev:.0f}/maand (geschat)\n"
    msg += f"   {generate_ascii_bar(total_rev, 500)}\n\n"

    # Activity
    prog_count = len(prog.get("generated_pages", []))
    bl_count = len(bl.get("opportunities", []))
    heal_fixes = healing.get("stats", {}).get("total_fixes", 0)

    msg += f"⚡ Activiteit:\n"
    msg += f"   Programmatic: {prog_count} pagina's\n"
    msg += f"   Backlinks:    {bl_count} kansen\n"
    msg += f"   Auto-fixes:   {heal_fixes} fixes\n"

    msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC"

    return msg


def generate_leaderboard():
    """Genereer een wekelijks artikel leaderboard."""
    conv = load_conversions()
    articles = conv.get("articles", {})

    if not articles:
        return "📊 Nog geen data voor leaderboard. Run /conversions eerst."

    sorted_arts = sorted(articles.items(), key=lambda x: x[1].get("conv_score", 0), reverse=True)

    msg = "🏆 ARTIKEL LEADERBOARD\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    max_score = sorted_arts[0][1]["conv_score"] if sorted_arts else 1

    for i, (slug, data) in enumerate(sorted_arts[:10]):
        medal = medals[i] if i < len(medals) else f"  "
        bar = generate_ascii_bar(data["conv_score"], max_score, 10)
        clicks = data.get("clicks", 0)
        rev = data.get("est_revenue", 0)
        msg += f"{medal} {slug[:25]}\n"
        msg += f"   {bar} {data['conv_score']:.0f}pts | {clicks}↗ | €{rev:.0f}\n"

    # Bottom 3 (need work)
    if len(sorted_arts) > 5:
        msg += f"\n📉 Verbetering nodig:\n"
        for slug, data in sorted_arts[-3:]:
            msg += f"  ⚠️ {slug[:30]}: {data['conv_score']:.0f}pts\n"

    return msg


def hive_mind_cycle():
    """Volledige Hive Mind cyclus — draait dagelijks."""
    actions = []

    # 1. Conversion intelligence update
    try:
        conv = analyze_article_conversions()
        top = conv.get("top_performers", [])
        if top:
            actions.append(f"📊 Conversions: top performer is {top[0]['slug'][:25]} ({top[0]['score']:.0f}pts)")
    except Exception as e:
        log(f"Conversion analysis error: {e}")

    # 2. Content DNA analyse (1x per week op maandag)
    if datetime.now().weekday() == 0:
        try:
            dna = analyze_content_dna()
            if dna:
                scores = dna.get("article_scores", {})
                avg = sum(scores.values()) / max(len(scores), 1)
                actions.append(f"🧬 DNA analyse: gem. match {avg:.0f}%")

                # Auto-improve slechtste DNA match
                worst = sorted(scores.items(), key=lambda x: x[1])
                if worst and worst[0][1] < 40:
                    improved = apply_dna_to_article(worst[0][0])
                    if improved:
                        actions.append(f"🧬 DNA-optimized: {improved}")
        except Exception as e:
            log(f"DNA analysis error: {e}")

    # 3. A/B test management
    try:
        ab_actions = check_ab2_tests()
        if ab_actions:
            actions.extend(ab_actions)
    except Exception as e:
        log(f"A/B test error: {e}")

    # 4. Backlink hunting (2x per week: dinsdag en vrijdag)
    if datetime.now().weekday() in [1, 4]:
        try:
            found, emails = backlink_batch()
            if found:
                actions.append(f"🔗 Backlinks: {found} kansen, {emails} outreach emails")
        except Exception as e:
            log(f"Backlink hunt error: {e}")

    return actions


# ── MODULE 13: OMNISCIENCE ENGINE ───────────────────────────────────────────
VALIDATOR_FILE = "/root/felix_hq/victor_validator.json"
FRESHNESS_FILE = "/root/felix_hq/victor_freshness.json"
JOURNEY_FILE = "/root/felix_hq/victor_journey.json"
DIGEST_FILE = "/root/felix_hq/victor_digest.json"
ROIGATE_FILE = "/root/felix_hq/victor_roigate.json"

def load_validator():
    if os.path.exists(VALIDATOR_FILE):
        try: return json.load(open(VALIDATOR_FILE))
        except: pass
    return {"checks": [], "failures": [], "last_check": None, "stats": {"total_checks": 0, "total_failures": 0}}

def save_validator(data):
    data["checks"] = data.get("checks", [])[-100:]
    data["failures"] = data.get("failures", [])[-50:]
    with open(VALIDATOR_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_freshness():
    if os.path.exists(FRESHNESS_FILE):
        try: return json.load(open(FRESHNESS_FILE))
        except: pass
    return {"articles": {}, "outdated": [], "auto_updated": [], "last_scan": None}

def save_freshness(data):
    data["outdated"] = data.get("outdated", [])[-100:]
    data["auto_updated"] = data.get("auto_updated", [])[-100:]
    with open(FRESHNESS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_journey():
    if os.path.exists(JOURNEY_FILE):
        try: return json.load(open(JOURNEY_FILE))
        except: pass
    return {"map": {}, "gaps": [], "coverage": {}, "last_analysis": None}

def save_journey(data):
    data["gaps"] = data.get("gaps", [])[-50:]
    with open(JOURNEY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_digest():
    if os.path.exists(DIGEST_FILE):
        try: return json.load(open(DIGEST_FILE))
        except: pass
    return {"pending_items": [], "sent_digests": [], "settings": {"min_priority": 3}}

def save_digest(data):
    data["pending_items"] = data.get("pending_items", [])[-200:]
    data["sent_digests"] = data.get("sent_digests", [])[-30:]
    with open(DIGEST_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_roigate():
    if os.path.exists(ROIGATE_FILE):
        try: return json.load(open(ROIGATE_FILE))
        except: pass
    return {"evaluations": [], "approved": [], "rejected": [], "threshold": 30}

def save_roigate(data):
    data["evaluations"] = data.get("evaluations", [])[-200:]
    data["approved"] = data.get("approved", [])[-100:]
    data["rejected"] = data.get("rejected", [])[-100:]
    with open(ROIGATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ── 13A: LIVE SITE VALIDATOR ────────────────────────────────────────────

def validate_live_page(slug):
    """Fetch en valideer een live pagina op aibuildermarketplace.com."""
    url = f"https://aibuildermarketplace.com/b2b/{slug}.html"
    issues = []

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'VictorBot/17.0 SiteValidator'
        })
        start = time.time()
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            load_time = time.time() - start
            content = response.read().decode('utf-8', errors='ignore')

            # 1. Status code
            if status != 200:
                issues.append({"type": "http_error", "detail": f"HTTP {status}", "severity": "critical"})

            # 2. Load time
            if load_time > 5:
                issues.append({"type": "slow", "detail": f"Laadtijd {load_time:.1f}s", "severity": "high"})
            elif load_time > 3:
                issues.append({"type": "slow", "detail": f"Laadtijd {load_time:.1f}s", "severity": "medium"})

            # 3. Empty page
            if len(content) < 200:
                issues.append({"type": "empty", "detail": f"Pagina bijna leeg ({len(content)} bytes)", "severity": "critical"})

            # 4. Affiliate links werken
            for brand, aff_url in VAULT.items():
                if brand.lower() in slug and aff_url not in content:
                    issues.append({"type": "missing_affiliate", "detail": f"Affiliate link {brand} ontbreekt", "severity": "high"})

            # 5. Title present
            if '<title>' not in content.lower():
                issues.append({"type": "no_title", "detail": "Geen title tag op live pagina", "severity": "high"})

            # 6. Content check — niet alleen boilerplate
            text = re.sub(r'<[^>]+>', '', content)
            if len(text.split()) < 100:
                issues.append({"type": "thin_content", "detail": f"Slechts {len(text.split())} woorden live", "severity": "high"})

            # 7. Broken images
            img_srcs = re.findall(r'<img[^>]*src="([^"]+)"', content, re.IGNORECASE)
            for src in img_srcs[:5]:  # Check max 5
                if src.startswith('http'):
                    try:
                        img_req = urllib.request.Request(src, method='HEAD', headers={'User-Agent': 'VictorBot/17.0'})
                        with urllib.request.urlopen(img_req, timeout=5) as img_resp:
                            if img_resp.status >= 400:
                                issues.append({"type": "broken_image", "detail": f"Broken image: {src[:50]}", "severity": "medium"})
                    except:
                        issues.append({"type": "broken_image", "detail": f"Image onbereikbaar: {src[:50]}", "severity": "medium"})

            return {"url": url, "status": status, "load_time": round(load_time, 2),
                    "size": len(content), "issues": issues, "ok": len(issues) == 0}

    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "load_time": 0, "size": 0,
                "issues": [{"type": "http_error", "detail": f"HTTP {e.code}", "severity": "critical"}], "ok": False}
    except Exception as e:
        return {"url": url, "status": 0, "load_time": 0, "size": 0,
                "issues": [{"type": "unreachable", "detail": f"Niet bereikbaar: {str(e)[:80]}", "severity": "critical"}], "ok": False}


def validate_full_site(max_pages=20):
    """Valideer alle live pagina's op de site."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return []

    files = [f.replace('.html', '') for f in os.listdir(b2b_path) if f.endswith('.html')]
    val = load_validator()
    results = []
    failures = []

    for slug in files[:max_pages]:
        result = validate_live_page(slug)
        results.append(result)
        if not result["ok"]:
            failures.append({
                "slug": slug,
                "issues": result["issues"],
                "date": str(datetime.now())
            })
        time.sleep(1)  # Rate limiting

    # Also validate main pages
    for main_page in ["", "b2b.html"]:
        url = f"https://aibuildermarketplace.com/{main_page}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'VictorBot/17.0'})
            start = time.time()
            with urllib.request.urlopen(req, timeout=15) as resp:
                load_time = time.time() - start
                results.append({"url": url, "status": resp.status, "load_time": round(load_time, 2),
                               "size": len(resp.read()), "issues": [], "ok": resp.status == 200})
        except Exception as e:
            results.append({"url": url, "status": 0, "load_time": 0, "size": 0,
                           "issues": [{"type": "error", "detail": str(e)[:80]}], "ok": False})

    val["checks"].append({
        "date": str(datetime.now()),
        "total": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"])
    })
    val["failures"].extend(failures)
    val["last_check"] = str(datetime.now())
    val["stats"]["total_checks"] = val["stats"].get("total_checks", 0) + len(results)
    val["stats"]["total_failures"] = val["stats"].get("total_failures", 0) + len(failures)
    save_validator(val)

    return results


# ── 13B: CONTENT FRESHNESS ENGINE ───────────────────────────────────────

# Zaken die snel verouderen in AI tool artikelen
FRESHNESS_SIGNALS = {
    "pricing": {
        "patterns": [r'\$\d+', r'€\d+', r'\d+\s*(per|/)\s*(month|maand|jaar|year)', r'free\s*plan', r'gratis\s*plan'],
        "max_age_days": 60,
        "severity": "high"
    },
    "features": {
        "patterns": [r'nieuw[e]?\s*feature', r'recent(ly)?\s*(added|toegevoegd)', r'just\s*launched', r'net\s*gelanceerd'],
        "max_age_days": 90,
        "severity": "medium"
    },
    "comparisons": {
        "patterns": [r'in\s*202[0-5]', r'anno\s*202[0-5]', r'as\s*of\s*202[0-5]'],
        "max_age_days": 180,
        "severity": "high"
    },
    "statistics": {
        "patterns": [r'\d+\s*miljoen\s*gebruikers', r'\d+\s*million\s*users', r'\d+%\s*(van|of|markt)'],
        "max_age_days": 120,
        "severity": "medium"
    }
}


def scan_article_freshness(slug):
    """Scan een enkel artikel op verouderde informatie."""
    filepath = f"{REPO_ROOT}/b2b/{slug}.html"
    if not os.path.exists(filepath):
        return None

    file_mtime = os.path.getmtime(filepath)
    file_age_days = (time.time() - file_mtime) / 86400

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    text = re.sub(r'<[^>]+>', '', content).lower()
    outdated_signals = []

    for signal_type, config in FRESHNESS_SIGNALS.items():
        for pattern in config["patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches and file_age_days > config["max_age_days"]:
                outdated_signals.append({
                    "type": signal_type,
                    "matches": matches[:3],
                    "severity": config["severity"],
                    "age_days": round(file_age_days),
                    "max_age": config["max_age_days"]
                })

    # Check for year references
    current_year = datetime.now().year
    old_years = re.findall(r'20(?:2[0-4]|1\d)', text)
    if old_years:
        outdated_signals.append({
            "type": "old_year",
            "matches": list(set(old_years)),
            "severity": "high",
            "detail": f"Verwijst naar {', '.join(set(old_years))} (nu {current_year})"
        })

    freshness_score = 100
    for signal in outdated_signals:
        if signal["severity"] == "critical":
            freshness_score -= 25
        elif signal["severity"] == "high":
            freshness_score -= 15
        elif signal["severity"] == "medium":
            freshness_score -= 8
    freshness_score = max(0, freshness_score)

    return {
        "slug": slug,
        "age_days": round(file_age_days),
        "freshness_score": freshness_score,
        "signals": outdated_signals,
        "needs_update": freshness_score < 60
    }


def auto_refresh_article(slug):
    """Automatisch een verouderd artikel updaten met actuele informatie."""
    filepath = f"{REPO_ROOT}/b2b/{slug}.html"
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    current_year = datetime.now().year

    # Stap 1: Simpele jaar-updates
    content_updated = content
    for old_year in range(2020, current_year):
        content_updated = content_updated.replace(str(old_year), str(current_year))

    # Stap 2: AI-gestuurde content refresh
    try:
        text = re.sub(r'<[^>]+>', '', content)[:3000]
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"""Je bent een content freshness expert. Dit artikel is verouderd.
Update het met actuele informatie voor {current_year}:
- Update alle jaartallen naar {current_year}
- Als er prijzen staan die oud lijken, markeer ze met [PRIJS CHECK NODIG]
- Update verouderde features of claims
- Behoud de volledige HTML structuur en styling
- Geef de VOLLEDIGE bijgewerkte HTML terug"""},
                {"role": "user", "content": content_updated[:5000]}
            ],
            max_tokens=4000,
            temperature=0.3
        )
        refreshed = res.choices[0].message.content.strip()
        if "```html" in refreshed:
            refreshed = refreshed.split("```html")[1].split("```")[0].strip()
        elif "```" in refreshed:
            refreshed = refreshed.split("```")[1].split("```")[0].strip()

        if len(refreshed) > 500:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(refreshed)

            run_command(f"cd {REPO_ROOT} && git add b2b/{slug}.html && git commit -m 'Victor: freshness update {slug}' && git push origin main")

            fresh = load_freshness()
            fresh["auto_updated"].append({"slug": slug, "date": str(datetime.now().date())})
            save_freshness(fresh)

            return slug
    except Exception as e:
        log(f"Freshness update error for {slug}: {e}")

    return None


def freshness_scan_batch(max_articles=10):
    """Scan alle artikelen op versheid en update de meest verouderde."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return [], []

    files = [f.replace('.html', '') for f in os.listdir(b2b_path) if f.endswith('.html')]
    fresh = load_freshness()
    results = []

    for slug in files[:max_articles * 2]:
        result = scan_article_freshness(slug)
        if result:
            results.append(result)
            fresh["articles"][slug] = {
                "freshness_score": result["freshness_score"],
                "age_days": result["age_days"],
                "needs_update": result["needs_update"],
                "date": str(datetime.now().date())
            }

    # Sort by freshness (lowest first)
    results.sort(key=lambda x: x["freshness_score"])
    outdated = [r for r in results if r["needs_update"]]
    fresh["outdated"] = [{"slug": r["slug"], "score": r["freshness_score"], "signals": len(r["signals"])} for r in outdated]
    fresh["last_scan"] = str(datetime.now())
    save_freshness(fresh)

    # Auto-update de 2 meest verouderde
    updated = []
    for r in outdated[:2]:
        result = auto_refresh_article(r["slug"])
        if result:
            updated.append(result)
            time.sleep(2)

    return outdated, updated


# ── 13C: BUYER JOURNEY MAPPER ───────────────────────────────────────────

JOURNEY_STAGES = {
    "awareness": {
        "signals": ["wat is", "what is", "uitleg", "introductie", "guide", "tutorial", "how to", "hoe werkt", "begrip"],
        "description": "Lezer ontdekt het probleem/tool voor het eerst"
    },
    "consideration": {
        "signals": ["vs", "versus", "vergelijk", "compare", "alternative", "alternatief", "review", "top", "beste", "best"],
        "description": "Lezer vergelijkt opties en overweegt keuzes"
    },
    "decision": {
        "signals": ["pricing", "kosten", "prijs", "kopen", "buy", "aanmelden", "signup", "kortingscode", "discount", "deal", "trial"],
        "description": "Lezer is klaar om te kopen/aan te melden"
    }
}


def map_buyer_journey():
    """Map alle artikelen naar buyer journey stages en vind gaten."""
    b2b_path = f"{REPO_ROOT}/b2b"
    if not os.path.isdir(b2b_path):
        return {}

    files = [f.replace('.html', '') for f in os.listdir(b2b_path) if f.endswith('.html')]
    journey = load_journey()
    journey_map = {}  # brand -> {stage: [slugs]}
    coverage = {}

    # Map elk artikel naar een stage
    article_stages = {}
    for slug in files:
        slug_lower = slug.lower()
        detected_stage = "awareness"  # Default

        for stage, config in JOURNEY_STAGES.items():
            for signal in config["signals"]:
                if signal in slug_lower:
                    detected_stage = stage
                    break

        # Detect brand
        detected_brand = "general"
        for brand in VAULT:
            if brand.lower() in slug_lower:
                detected_brand = brand
                break

        article_stages[slug] = {"stage": detected_stage, "brand": detected_brand}

        if detected_brand not in journey_map:
            journey_map[detected_brand] = {"awareness": [], "consideration": [], "decision": []}
        journey_map[detected_brand][detected_stage].append(slug)

    # Analyseer gaten
    gaps = []
    for brand in VAULT:
        if brand not in journey_map:
            journey_map[brand] = {"awareness": [], "consideration": [], "decision": []}

        brand_map = journey_map[brand]
        total = sum(len(v) for v in brand_map.values())

        coverage[brand] = {
            "awareness": len(brand_map["awareness"]),
            "consideration": len(brand_map["consideration"]),
            "decision": len(brand_map["decision"]),
            "total": total,
            "complete": all(len(v) > 0 for v in brand_map.values())
        }

        # Vind ontbrekende stages
        for stage in ["awareness", "consideration", "decision"]:
            if not brand_map[stage]:
                # Genereer artikel suggestie per stage
                if stage == "awareness":
                    suggestion = f"wat-is-{brand.lower()}-uitleg"
                    title = f"Wat is {brand}? Complete Uitleg & Guide"
                elif stage == "consideration":
                    suggestion = f"beste-{brand.lower()}-alternatieven"
                    title = f"Beste {brand} Alternatieven: Top 5 Vergeleken"
                else:
                    suggestion = f"{brand.lower()}-pricing-kosten"
                    title = f"{brand} Pricing & Kosten: Compleet Overzicht"

                gaps.append({
                    "brand": brand,
                    "missing_stage": stage,
                    "suggested_slug": suggestion,
                    "suggested_title": title,
                    "priority": "high" if stage == "decision" else "medium",
                    "reason": f"{brand} mist {stage} content — potentiële conversies gaan verloren"
                })

    journey["map"] = {brand: {stage: slugs for stage, slugs in stages.items()}
                      for brand, stages in journey_map.items() if brand in VAULT}
    journey["gaps"] = gaps
    journey["coverage"] = coverage
    journey["article_stages"] = article_stages
    journey["last_analysis"] = str(datetime.now())
    save_journey(journey)

    return journey


def auto_fill_journey_gap(max_articles=1):
    """Schrijf automatisch artikelen om journey gaten te vullen."""
    journey = load_journey()
    gaps = journey.get("gaps", [])

    if not gaps:
        journey = map_buyer_journey()
        gaps = journey.get("gaps", [])

    if not gaps:
        return []

    # Prioriteer: decision > consideration > awareness
    priority_order = {"decision": 0, "consideration": 1, "awareness": 2}
    gaps.sort(key=lambda g: priority_order.get(g.get("missing_stage", ""), 3))

    written = []
    for gap in gaps[:max_articles]:
        slug = gap["suggested_slug"]
        filepath = f"{REPO_ROOT}/b2b/{slug}.html"
        if os.path.exists(filepath):
            continue

        brand = gap["brand"]
        stage = gap["missing_stage"]
        title = gap["suggested_title"]

        stage_prompt = {
            "awareness": f"Schrijf een informatief artikel dat uitlegt wat {brand} is, hoe het werkt, en voor wie het geschikt is. Focus op educatie, niet verkoop.",
            "consideration": f"Schrijf een vergelijkingsartikel: {brand} vs de top alternatieven. Objectief, eerlijk, met voor- en nadelen per optie.",
            "decision": f"Schrijf een pricing/kosten artikel over {brand}. Alle plans, verborgen kosten, ROI analyse, en de beste deal tips. Focus op het helpen van de lezer om een beslissing te nemen."
        }

        aff_info = f"Affiliate link {brand}: {VAULT.get(brand, 'N/A')}\n"
        aff_info += "\n".join([f"{b}: {u}" for b, u in VAULT.items() if b != brand])

        try:
            res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Je bent een SEO content expert. Schrijf complete HTML artikelen met dark theme styling. Professioneel, informatief, 2000+ woorden."},
                    {"role": "user", "content": f"Titel: {title}\n\n{stage_prompt[stage]}\n\nAffiliate links:\n{aff_info}\n\nDark theme HTML, 2000-3000 woorden."}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            html = res.choices[0].message.content.strip()
            if "```html" in html:
                html = html.split("```html")[1].split("```")[0].strip()
            elif "```" in html:
                html = html.split("```")[1].split("```")[0].strip()

            os.makedirs(f"{REPO_ROOT}/b2b", exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Schema toevoegen
            try:
                add_schema_to_article(filepath)
            except:
                pass

            written.append(f"{slug} ({brand} {stage})")
            time.sleep(2)
        except Exception as e:
            log(f"Journey gap fill error: {e}")

    if written:
        try:
            rebuild_sitemap()
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: journey gap fill — {len(written)} articles' && git push origin main")
        except:
            pass

    return written


# ── 13D: SMART DIGEST SYSTEM ────────────────────────────────────────────

def add_digest_item(category, message, priority=5, data=None):
    """Voeg een item toe aan de dagelijkse digest. Priority: 1=laag, 10=kritiek."""
    digest = load_digest()
    digest["pending_items"].append({
        "category": category,
        "message": message,
        "priority": priority,
        "data": data or {},
        "time": str(datetime.now())
    })
    save_digest(digest)


def generate_smart_digest():
    """Genereer één intelligente dagelijkse digest van alle activiteit."""
    digest = load_digest()
    items = digest.get("pending_items", [])

    if not items:
        return None

    # Sorteer op prioriteit (hoogste eerst)
    items.sort(key=lambda x: x.get("priority", 5), reverse=True)

    # Groepeer per categorie
    categories = {}
    for item in items:
        cat = item.get("category", "overig")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    # Bouw digest
    msg = f"📋 VICTOR DAILY DIGEST\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📅 {datetime.now().strftime('%A %d %B %Y')}\n\n"

    # Priority items eerst
    critical = [i for i in items if i.get("priority", 0) >= 8]
    if critical:
        msg += "🚨 ACTIE VEREIST:\n"
        for item in critical[:5]:
            msg += f"  ❗ {item['message']}\n"
        msg += "\n"

    # Category summaries
    category_emojis = {
        "seo": "📈", "revenue": "💰", "content": "📝", "technical": "🔧",
        "competitor": "🕵️", "growth": "🚀", "healing": "🏥", "backlinks": "🔗",
        "freshness": "🔄", "journey": "🗺️", "overig": "📌"
    }

    for cat, cat_items in categories.items():
        emoji = category_emojis.get(cat, "📌")
        msg += f"{emoji} {cat.upper()} ({len(cat_items)}):\n"
        for item in cat_items[:3]:
            prio_dot = "🔴" if item["priority"] >= 8 else "🟡" if item["priority"] >= 5 else "🟢"
            msg += f"  {prio_dot} {item['message'][:70]}\n"
        if len(cat_items) > 3:
            msg += f"  ... en {len(cat_items) - 3} meer\n"
        msg += "\n"

    # Summary stats
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 Totaal: {len(items)} items | "
    msg += f"🔴 {len([i for i in items if i['priority'] >= 8])} kritiek | "
    msg += f"🟡 {len([i for i in items if 5 <= i['priority'] < 8])} medium | "
    msg += f"🟢 {len([i for i in items if i['priority'] < 5])} laag"

    # Clear pending items
    digest["pending_items"] = []
    digest["sent_digests"].append({
        "date": str(datetime.now()),
        "items_count": len(items),
        "critical_count": len(critical)
    })
    save_digest(digest)

    return msg


# ── 13E: ROI GATE ───────────────────────────────────────────────────────

def evaluate_article_roi(keyword, brand=None):
    """Evalueer de ROI van een artikel VOORDAT het geschreven wordt."""
    roi = load_roigate()

    score = 0
    factors = []
    estimates = {}

    # 1. Keyword competition analyse
    keyword_lower = keyword.lower()

    # High-value keyword types
    if 'vs' in keyword_lower:
        score += 20
        factors.append("VS-artikel: laag concurrentie, hoog koopintentie")
    elif 'alternative' in keyword_lower or 'alternatief' in keyword_lower:
        score += 18
        factors.append("Alternatieven: hoge koopintentie")
    elif 'pricing' in keyword_lower or 'kosten' in keyword_lower:
        score += 22
        factors.append("Pricing: hoogste koopintentie, dichtbij conversie")
    elif 'review' in keyword_lower:
        score += 15
        factors.append("Review: goede koopintentie")
    elif 'how' in keyword_lower or 'tutorial' in keyword_lower or 'hoe' in keyword_lower:
        score += 8
        factors.append("How-to: breed publiek maar lage koopintentie")
    else:
        score += 5
        factors.append("Informatief: onzeker conversie-potentieel")

    # 2. Brand commission value
    if brand and brand in COMMISSION_RATES:
        rates = COMMISSION_RATES[brand]
        commission = rates.get("per_signup", 0)
        if commission >= 50:
            score += 25
            factors.append(f"Hoge commissie: €{commission}/signup")
        elif commission >= 15:
            score += 15
            factors.append(f"Gemiddelde commissie: €{commission}/signup")
        else:
            score += 8
            factors.append(f"Lage commissie: €{commission}/signup")
        estimates["commission_per_signup"] = commission
    elif brand:
        for b, rates in COMMISSION_RATES.items():
            if b.lower() in keyword_lower:
                commission = rates.get("per_signup", 0)
                score += min(commission, 25)
                factors.append(f"Commissie {b}: €{commission}/signup")
                estimates["commission_per_signup"] = commission
                brand = b
                break

    # 3. Existing coverage check
    b2b_path = f"{REPO_ROOT}/b2b"
    similar_exists = False
    if os.path.isdir(b2b_path):
        for f in os.listdir(b2b_path):
            f_slug = f.replace('.html', '').lower()
            keywords = keyword_lower.replace('-', ' ').split()
            overlap = sum(1 for w in keywords if w in f_slug)
            if overlap >= len(keywords) * 0.7:
                similar_exists = True
                score -= 10
                factors.append(f"⚠️ Vergelijkbaar artikel bestaat: {f_slug[:30]}")
                break

    if not similar_exists:
        score += 10
        factors.append("Nieuw topic — geen overlap")

    # 4. GSC data (als beschikbaar)
    if os.path.exists(GSC_DATA_FILE):
        try:
            with open(GSC_DATA_FILE) as f:
                gsc = json.load(f)
            # Check of we al impressions hebben voor gerelateerde queries
            relevant_queries = [q for q in gsc.get("queries", [])
                               if any(w in q.get("query", "").lower() for w in keyword_lower.split('-'))]
            if relevant_queries:
                total_impr = sum(q.get("impressions", 0) for q in relevant_queries)
                if total_impr > 100:
                    score += 10
                    factors.append(f"GSC data: {total_impr} impressions voor gerelateerde queries")
                    estimates["existing_impressions"] = total_impr
        except:
            pass

    # 5. Ranking prediction (use existing function)
    try:
        pred_score, pred_factors = predict_ranking_success(keyword, brand or keyword.split('-')[0].title())
        ranking_bonus = pred_score // 10
        score += ranking_bonus
        factors.append(f"Ranking voorspelling: {pred_score}/100")
        estimates["ranking_prediction"] = pred_score
    except:
        pass

    # Revenue estimate
    est_monthly_clicks = 50 if score > 60 else 20 if score > 40 else 5
    est_ctr = COMMISSION_RATES.get(brand, {}).get("est_ctr", 0.02) if brand else 0.015
    est_commission = estimates.get("commission_per_signup", 10)
    est_monthly_revenue = est_monthly_clicks * est_ctr * est_commission

    estimates["monthly_clicks"] = est_monthly_clicks
    estimates["affiliate_ctr"] = est_ctr
    estimates["monthly_revenue"] = round(est_monthly_revenue, 2)
    estimates["yearly_revenue"] = round(est_monthly_revenue * 12, 2)
    estimates["time_to_rank_months"] = 2 if score > 60 else 4 if score > 40 else 8

    # Final evaluation
    threshold = roi.get("threshold", 30)
    approved = score >= threshold

    evaluation = {
        "keyword": keyword,
        "brand": brand,
        "score": score,
        "factors": factors,
        "estimates": estimates,
        "approved": approved,
        "date": str(datetime.now()),
        "threshold": threshold
    }

    roi["evaluations"].append(evaluation)
    if approved:
        roi["approved"].append({"keyword": keyword, "score": score, "date": str(datetime.now().date())})
    else:
        roi["rejected"].append({"keyword": keyword, "score": score, "date": str(datetime.now().date()),
                                "reason": "Score onder threshold"})
    save_roigate(roi)

    return evaluation


def omniscience_cycle():
    """Volledige Omniscience cyclus — draait dagelijks."""
    actions = []

    # 1. Live site validatie (steekproef)
    try:
        results = validate_full_site(max_pages=5)
        passed = sum(1 for r in results if r["ok"])
        failed = sum(1 for r in results if not r["ok"])
        if failed:
            actions.append(f"🔍 Site validatie: {failed} pagina's met problemen")
            add_digest_item("technical", f"Site validatie: {failed}/{len(results)} pagina's falen", priority=8 if failed > 2 else 6)
        else:
            actions.append(f"✅ Site validatie: alle {passed} pagina's OK")
    except Exception as e:
        log(f"Validator error: {e}")

    # 2. Freshness scan
    try:
        outdated, updated = freshness_scan_batch(max_articles=10)
        if outdated:
            actions.append(f"🔄 Freshness: {len(outdated)} verouderde artikelen, {len(updated)} auto-updated")
            if len(outdated) > 3:
                add_digest_item("freshness", f"{len(outdated)} artikelen verouderd — {len(updated)} auto-updated", priority=6)
        else:
            actions.append("✅ Alle content is up-to-date")
    except Exception as e:
        log(f"Freshness error: {e}")

    # 3. Buyer journey analyse (1x per week op donderdag)
    if datetime.now().weekday() == 3:
        try:
            journey = map_buyer_journey()
            gaps = journey.get("gaps", [])
            if gaps:
                actions.append(f"🗺️ Journey: {len(gaps)} gaten in buyer journey")
                add_digest_item("journey", f"Buyer journey: {len(gaps)} gaten gevonden", priority=7)

                # Auto-fill 1 gap
                filled = auto_fill_journey_gap(max_articles=1)
                if filled:
                    actions.append(f"🗺️ Journey gap gevuld: {', '.join(filled)}")
            else:
                actions.append("✅ Buyer journey compleet voor alle brands")
        except Exception as e:
            log(f"Journey error: {e}")

    return actions


# ── MODULE 14: SKYNET PROTOCOL ──────────────────────────────────────────────
CALENDAR_FILE = "/root/felix_hq/victor_calendar.json"
PALACE_FILE = "/root/felix_hq/victor_palace.json"
OUTREACH_FILE = "/root/felix_hq/victor_outreach.json"
API_LOG_FILE = "/root/felix_hq/victor_api.log"
API_PORT = 5151

def load_calendar():
    if os.path.exists(CALENDAR_FILE):
        try: return json.load(open(CALENDAR_FILE))
        except: pass
    return {"planned": [], "executed": [], "queue": [], "settings": {"max_daily": 3, "auto_execute": True}}

def save_calendar(data):
    data["planned"] = data.get("planned", [])[-200:]
    data["executed"] = data.get("executed", [])[-200:]
    with open(CALENDAR_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_palace():
    if os.path.exists(PALACE_FILE):
        try: return json.load(open(PALACE_FILE))
        except: pass
    return {"seasonal_patterns": {}, "brand_trends": {}, "content_performance": {},
            "quarterly_insights": [], "strategic_memory": [], "last_update": None}

def save_palace(data):
    data["quarterly_insights"] = data.get("quarterly_insights", [])[-20:]
    data["strategic_memory"] = data.get("strategic_memory", [])[-50:]
    with open(PALACE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_outreach():
    if os.path.exists(OUTREACH_FILE):
        try: return json.load(open(OUTREACH_FILE))
        except: pass
    return {"campaigns": [], "sent": [], "responses": [], "stats": {"total_sent": 0, "responses": 0, "links_gained": 0}}

def save_outreach(data):
    data["campaigns"] = data.get("campaigns", [])[-100:]
    data["sent"] = data.get("sent", [])[-200:]
    with open(OUTREACH_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ── 14A: VICTOR API SERVER ──────────────────────────────────────────────

def api_log(msg):
    """Log API events."""
    try:
        with open(API_LOG_FILE, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except:
        pass


def start_api_server():
    """Start een lightweight HTTP API server voor webhooks."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json as json_mod

    class VictorAPIHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            api_log(f"HTTP {args[0] if args else ''}")

        def _send_json(self, code, data):
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_mod.dumps(data).encode())

        def do_GET(self):
            path = self.path.split('?')[0]

            if path == '/api/health':
                self._send_json(200, {
                    "status": "online",
                    "version": "15.0",
                    "uptime": "active",
                    "model": MODEL,
                    "timestamp": datetime.now().isoformat()
                })

            elif path == '/api/stats':
                b2b_path = f"{REPO_ROOT}/b2b"
                article_count = len([f for f in os.listdir(b2b_path) if f.endswith('.html')]) if os.path.isdir(b2b_path) else 0
                en_path = f"{REPO_ROOT}/en"
                en_count = len([f for f in os.listdir(en_path) if f.endswith('.html')]) if os.path.isdir(en_path) else 0

                serp = load_serp_data()
                tracking = serp.get("tracking", {})
                page1 = sum(1 for s, d in tracking.items() if d.get("positions") and d["positions"][-1]["pos"] <= 10)

                conv = load_conversions()
                total_rev = sum(a.get("est_revenue", 0) for a in conv.get("articles", {}).values())

                self._send_json(200, {
                    "articles": {"nl": article_count, "en": en_count},
                    "rankings": {"tracked": len(tracking), "page1": page1},
                    "revenue": {"estimated_monthly": round(total_rev, 2)},
                    "timestamp": datetime.now().isoformat()
                })

            elif path == '/api/serp':
                serp = load_serp_data()
                tracking = serp.get("tracking", {})
                data = {}
                for slug, d in tracking.items():
                    if d.get("positions"):
                        last = d["positions"][-1]
                        data[slug] = {"position": last["pos"], "clicks": last.get("clicks", 0),
                                     "trend": d.get("trend", "unknown")}
                self._send_json(200, data)

            elif path == '/api/calendar':
                cal = load_calendar()
                self._send_json(200, cal)

            elif path == '/api/palace':
                palace = load_palace()
                self._send_json(200, {
                    "seasonal_patterns": palace.get("seasonal_patterns", {}),
                    "brand_trends": palace.get("brand_trends", {}),
                    "strategic_memory": palace.get("strategic_memory", [])[-5:]
                })

            else:
                self._send_json(404, {"error": "Not found", "endpoints": [
                    "/api/health", "/api/stats", "/api/serp", "/api/calendar", "/api/palace"
                ]})

        def do_POST(self):
            path = self.path.split('?')[0]
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8', errors='ignore') if content_len else '{}'

            try:
                payload = json_mod.loads(body) if body else {}
            except:
                payload = {}

            if path == '/api/webhook/github':
                # GitHub deploy webhook → auto validate
                api_log(f"GitHub webhook received: {payload.get('ref', 'unknown')}")
                try:
                    # Trigger validatie na deploy
                    threading.Thread(target=self._post_deploy_validate, daemon=True).start()
                    self._send_json(200, {"status": "accepted", "action": "post_deploy_validation_started"})
                except Exception as e:
                    self._send_json(500, {"error": str(e)})

            elif path == '/api/webhook/uptime':
                # Externe uptime monitor webhook
                api_log(f"Uptime webhook: {payload}")
                status = payload.get("status", "unknown")
                if status in ["down", "error"]:
                    try:
                        bot.send_message(ADMIN_ID, f"🚨 Uptime Alert: Site is {status}!")
                        add_digest_item("technical", f"Uptime alert: site {status}", priority=10)
                    except:
                        pass
                self._send_json(200, {"status": "received"})

            elif path == '/api/trigger':
                # Trigger een specifieke actie
                action = payload.get("action", "")
                api_log(f"Trigger: {action}")
                if action == "validate":
                    threading.Thread(target=self._post_deploy_validate, daemon=True).start()
                    self._send_json(200, {"status": "validation_started"})
                elif action == "digest":
                    digest = generate_smart_digest()
                    self._send_json(200, {"digest": digest or "No items"})
                elif action == "scorecard":
                    sc = generate_scorecard()
                    self._send_json(200, {"scorecard": sc})
                else:
                    self._send_json(400, {"error": f"Unknown action: {action}"})

            else:
                self._send_json(404, {"error": "Not found"})

        def _post_deploy_validate(self):
            """Na een deploy, wacht even en valideer dan de site."""
            time.sleep(30)  # Wacht tot GitHub Pages updated
            try:
                results = validate_full_site(max_pages=10)
                failed = [r for r in results if not r["ok"]]
                if failed:
                    msg = f"🚨 Post-Deploy Validatie — {len(failed)} problemen!\n\n"
                    for r in failed[:5]:
                        slug = r["url"].split("/")[-1]
                        issues = ", ".join(i["detail"][:30] for i in r["issues"][:2])
                        msg += f"  ❌ {slug}: {issues}\n"
                    bot.send_message(ADMIN_ID, msg)
                    add_digest_item("technical", f"Deploy validatie: {len(failed)} problemen", priority=8)
                else:
                    api_log(f"Post-deploy validation passed: {len(results)} pages OK")
            except Exception as e:
                api_log(f"Post-deploy validation error: {e}")

    try:
        server = HTTPServer(('0.0.0.0', API_PORT), VictorAPIHandler)
        server.timeout = 5
        api_log(f"API server starting on port {API_PORT}")

        while True:
            server.handle_request()
    except Exception as e:
        api_log(f"API server error: {e}")


# ── 14B: EMAIL OUTREACH SYSTEM ──────────────────────────────────────────

def send_outreach_email(to_email, subject, body, campaign_id=None):
    """Verstuur een outreach email via SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # SMTP config uit env
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_email = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_host or not smtp_user:
        return False, "SMTP niet geconfigureerd. Set SMTP_HOST, SMTP_USER, SMTP_PASS in .env"

    try:
        msg = MIMEMultipart()
        msg['From'] = f"AI Builder Marketplace <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        # Track
        outreach = load_outreach()
        outreach["sent"].append({
            "to": to_email,
            "subject": subject,
            "campaign_id": campaign_id,
            "date": str(datetime.now()),
            "status": "sent"
        })
        outreach["stats"]["total_sent"] = outreach["stats"].get("total_sent", 0) + 1
        save_outreach(outreach)

        return True, "Email verstuurd"
    except Exception as e:
        return False, str(e)


def run_outreach_campaign(max_emails=3):
    """Voer een outreach campagne uit: stuur emails naar gevonden kansen."""
    bl = load_backlinks()
    outreach = load_outreach()

    # Vind kansen met emails klaar maar nog niet verstuurd
    ready = [o for o in bl.get("opportunities", [])
             if o.get("outreach_email") and o.get("status") == "email_ready"]

    already_sent = {s["to"] for s in outreach.get("sent", [])}
    sent_count = 0
    results = []

    for opp in ready[:max_emails]:
        # Extract email uit URL (simpele heuristiek)
        domain = ""
        try:
            domain = opp["url"].split("//")[1].split("/")[0]
        except:
            continue

        # Genereer contact email (common patterns)
        contact_emails = [
            f"hello@{domain}",
            f"contact@{domain}",
            f"info@{domain}"
        ]

        for email in contact_emails:
            if email in already_sent:
                continue

            # Parse subject en body uit gegenereerde email
            email_content = opp["outreach_email"]
            lines = email_content.strip().split('\n')
            subject = lines[0].replace("Subject:", "").strip() if lines else f"Content collaboration — AI Builder Marketplace"
            body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else email_content

            success, msg = send_outreach_email(email, subject, body, campaign_id=opp.get("url"))
            if success:
                opp["status"] = "email_sent"
                sent_count += 1
                results.append(f"✉️ {domain}: verstuurd")
            else:
                results.append(f"❌ {domain}: {msg[:50]}")

            break  # 1 email per domein

    if sent_count:
        save_backlinks(bl)

    return results


# ── 14C: UNIFIED CONTENT CALENDAR ───────────────────────────────────────

def generate_content_calendar():
    """Genereer een intelligent content kalender op basis van alle data bronnen."""
    cal = load_calendar()
    today = datetime.now()
    planned = []

    # Bron 1: Journey gaten (hoogste prioriteit)
    try:
        journey = load_journey()
        for gap in journey.get("gaps", [])[:3]:
            planned.append({
                "type": "journey_gap",
                "slug": gap["suggested_slug"],
                "title": gap["suggested_title"],
                "brand": gap["brand"],
                "stage": gap["missing_stage"],
                "priority": 9 if gap["missing_stage"] == "decision" else 7,
                "source": "buyer_journey",
                "scheduled_date": str((today + timedelta(days=len(planned) + 1)).date()),
                "reason": gap["reason"]
            })
    except:
        pass

    # Bron 2: Trending topics (hoge urgentie)
    try:
        trends = load_trends()
        hot = [t for t in trends.get("detected", [])
               if t.get("urgency") == "high" and t.get("article_idea")
               and t.get("source") == "ai_analysis"]
        written = {a["topic"] for a in trends.get("articles_written", [])}
        for t in hot[:2]:
            if t.get("article_idea", "") not in written:
                slug = re.sub(r'[^a-z0-9-]', '', t["article_idea"].lower().replace(' ', '-'))[:50]
                planned.append({
                    "type": "trending",
                    "slug": slug,
                    "title": t["article_idea"],
                    "priority": 8,
                    "source": "trend_radar",
                    "scheduled_date": str((today + timedelta(days=1)).date()),
                    "reason": f"Trending topic: {t.get('keyword', 'AI')}"
                })
    except:
        pass

    # Bron 3: Freshness updates (medium prioriteit)
    try:
        fresh = load_freshness()
        outdated = fresh.get("outdated", [])
        for o in outdated[:2]:
            planned.append({
                "type": "freshness_update",
                "slug": o["slug"],
                "title": f"Update: {o['slug'].replace('-', ' ').title()}",
                "priority": 6,
                "source": "freshness_engine",
                "scheduled_date": str((today + timedelta(days=len(planned) + 2)).date()),
                "reason": f"Freshness score: {o.get('score', '?')}/100"
            })
    except:
        pass

    # Bron 4: Programmatic SEO (bulk)
    try:
        combos = generate_programmatic_combinations()
        b2b_path = f"{REPO_ROOT}/b2b"
        new_combos = [c for c in combos if not os.path.exists(f"{b2b_path}/{c['slug']}.html")]
        for c in new_combos[:2]:
            planned.append({
                "type": "programmatic",
                "slug": c["slug"],
                "title": c["title"],
                "brand": c.get("brand_a", c.get("brand", "")),
                "priority": 5,
                "source": "programmatic_seo",
                "scheduled_date": str((today + timedelta(days=len(planned) + 3)).date()),
                "reason": f"Programmatic: {c['type']} template"
            })
    except:
        pass

    # Bron 5: ROI Gate evaluatie op alle planned items
    roi_filtered = []
    for item in planned:
        try:
            brand = item.get("brand", item["slug"].split('-')[0].title())
            evaluation = evaluate_article_roi(item["slug"], brand)
            item["roi_score"] = evaluation["score"]
            item["roi_approved"] = evaluation["approved"]
            item["est_revenue"] = evaluation.get("estimates", {}).get("monthly_revenue", 0)
            if evaluation["approved"] or item["priority"] >= 8:
                roi_filtered.append(item)
        except:
            roi_filtered.append(item)

    # Sorteer op prioriteit + ROI
    roi_filtered.sort(key=lambda x: (x.get("priority", 0) * 2 + x.get("roi_score", 0)), reverse=True)

    # Memory Palace insights toepassen
    try:
        palace = load_palace()
        current_month = today.strftime("%B").lower()
        seasonal = palace.get("seasonal_patterns", {}).get(current_month, {})
        if seasonal.get("best_content_type"):
            # Boost items die matchen met seizoenspatronen
            for item in roi_filtered:
                if seasonal["best_content_type"] in item.get("type", ""):
                    item["priority"] += 1
    except:
        pass

    # Save
    cal["planned"] = roi_filtered[:14]  # Max 2 weken vooruit
    cal["queue"] = [item["slug"] for item in roi_filtered[:14]]
    save_calendar(cal)

    return cal


def execute_calendar_item():
    """Voer het eerstvolgende item uit de content calendar uit."""
    cal = load_calendar()
    planned = cal.get("planned", [])

    if not planned:
        generate_content_calendar()
        cal = load_calendar()
        planned = cal.get("planned", [])

    if not planned:
        return None, "Geen items in calendar"

    # Pak het item met hoogste prioriteit dat nog niet is uitgevoerd
    executed_slugs = {e["slug"] for e in cal.get("executed", [])}
    next_item = None
    for item in planned:
        if item["slug"] not in executed_slugs:
            next_item = item
            break

    if not next_item:
        return None, "Alle items zijn al uitgevoerd"

    slug = next_item["slug"]
    item_type = next_item["type"]
    result = None

    if item_type == "freshness_update":
        result = auto_refresh_article(slug)
    elif item_type == "journey_gap":
        filled = auto_fill_journey_gap(max_articles=1)
        result = filled[0] if filled else None
    elif item_type == "trending":
        result = auto_write_trend_article()
    elif item_type == "programmatic":
        combo = None
        for c in generate_programmatic_combinations():
            if c["slug"] == slug:
                combo = c
                break
        if combo:
            result = generate_programmatic_page(combo)
    else:
        # Default: schrijf via Claude
        try:
            aff_info = "\n".join(f"{b}: {u}" for b, u in VAULT.items())
            res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Schrijf een professioneel SEO artikel. Dark theme HTML, 2000+ woorden."},
                    {"role": "user", "content": f"Titel: {next_item['title']}\n\nAffiliate links:\n{aff_info}"}
                ],
                max_tokens=4000, temperature=0.7
            )
            html = res.choices[0].message.content.strip()
            if "```html" in html:
                html = html.split("```html")[1].split("```")[0].strip()
            elif "```" in html:
                html = html.split("```")[1].split("```")[0].strip()
            filepath = f"{REPO_ROOT}/b2b/{slug}.html"
            os.makedirs(f"{REPO_ROOT}/b2b", exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            try:
                add_schema_to_article(filepath)
            except: pass
            rebuild_sitemap()
            run_command(f"cd {REPO_ROOT} && git add -A && git commit -m 'Victor: calendar — {slug}' && git push origin main")
            result = slug
        except Exception as e:
            log(f"Calendar execute error: {e}")

    if result:
        cal["executed"].append({
            "slug": slug,
            "type": item_type,
            "title": next_item.get("title", ""),
            "date": str(datetime.now()),
            "priority": next_item.get("priority", 0)
        })
        # Remove from planned
        cal["planned"] = [p for p in cal["planned"] if p["slug"] != slug]
        save_calendar(cal)

    return result, next_item


# ── 14D: LIVE DASHBOARD V2 ──────────────────────────────────────────────

def generate_dashboard_v2():
    """Genereer een real-time dashboard met Chart.js en live data."""
    # Gather data
    b2b_path = f"{REPO_ROOT}/b2b"
    article_count = len([f for f in os.listdir(b2b_path) if f.endswith('.html')]) if os.path.isdir(b2b_path) else 0
    en_path = f"{REPO_ROOT}/en"
    en_count = len([f for f in os.listdir(en_path) if f.endswith('.html')]) if os.path.isdir(en_path) else 0

    serp = load_serp_data()
    tracking = serp.get("tracking", {})
    snapshots = serp.get("daily_snapshots", [])[-30:]

    conv = load_conversions()
    top_performers = conv.get("top_performers", [])[:10]

    audit = load_audit()
    audit_scores = audit.get("scores", {})

    cal = load_calendar()
    palace = load_palace()

    healing = load_healing()
    uptime_checks = healing.get("uptime_checks", [])[-24:]

    # SERP chart data
    serp_dates = [s.get("date", "") for s in snapshots]
    serp_page1 = [s.get("page1", 0) for s in snapshots]
    serp_top3 = [s.get("top3", 0) for s in snapshots]

    # Uptime chart data
    uptime_times = [c.get("time", "")[-8:-3] for c in uptime_checks]
    uptime_values = [c.get("response_time", 0) for c in uptime_checks]

    # Top performers data
    tp_labels = [t.get("slug", "")[:20] for t in top_performers]
    tp_scores = [t.get("score", 0) for t in top_performers]

    # Audit score history
    audit_dates = list(audit_scores.keys())[-14:]
    audit_vals = [audit_scores[d] for d in audit_dates]

    dashboard_html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Victor 17.0 Omega — Command Center</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0a0a1a; color: #e0e0ff; font-family: 'Segoe UI', sans-serif; padding: 20px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; }}
.card {{ background: #12122a; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; }}
.card h3 {{ color: #6c63ff; margin-bottom: 15px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
.stat {{ font-size: 36px; font-weight: bold; color: #fff; }}
.stat-label {{ font-size: 12px; color: #888; margin-top: 4px; }}
.stat-row {{ display: flex; justify-content: space-between; margin-bottom: 15px; }}
.stat-box {{ text-align: center; }}
.header {{ text-align: center; padding: 20px 0 30px; }}
.header h1 {{ font-size: 28px; color: #6c63ff; }}
.header p {{ color: #666; margin-top: 5px; }}
.mini-stat {{ display: inline-block; background: #1a1a3a; padding: 8px 16px; border-radius: 20px; margin: 5px; font-size: 13px; }}
canvas {{ max-height: 200px; }}
.planned {{ list-style: none; padding: 0; }}
.planned li {{ padding: 8px 0; border-bottom: 1px solid #1a1a3a; font-size: 13px; }}
.planned .prio {{ color: #6c63ff; font-weight: bold; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; }}
.badge-ok {{ background: #1a3a1a; color: #4caf50; }}
.badge-warn {{ background: #3a3a1a; color: #ff9800; }}
.badge-err {{ background: #3a1a1a; color: #f44336; }}
.refresh {{ position: fixed; bottom: 20px; right: 20px; background: #6c63ff; color: #fff; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; }}
</style>
</head>
<body>
<div class="header">
<h1>Victor 17.0 Omega — Command Center</h1>
<p>Real-time dashboard | Last update: {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC</p>
<div style="margin-top:15px;">
<span class="mini-stat">📝 {article_count} NL</span>
<span class="mini-stat">🌍 {en_count} EN</span>
<span class="mini-stat">📈 {sum(1 for s,d in tracking.items() if d.get('positions') and d['positions'][-1]['pos']<=10)} Pagina 1</span>
<span class="mini-stat">💰 €{sum(a.get('est_revenue',0) for a in conv.get('articles',{}).values()):.0f}/mo</span>
</div>
</div>

<div class="grid">
<div class="card">
<h3>📈 SERP Posities (30 dagen)</h3>
<canvas id="serpChart"></canvas>
</div>
<div class="card">
<h3>🏆 Top Performers</h3>
<canvas id="performersChart"></canvas>
</div>
<div class="card">
<h3>⚡ Response Time (24h)</h3>
<canvas id="uptimeChart"></canvas>
</div>
<div class="card">
<h3>🔍 SEO Health Score</h3>
<canvas id="auditChart"></canvas>
</div>
<div class="card">
<h3>📋 Content Calendar</h3>
<ul class="planned">
{''.join(f'<li><span class="prio">[{p.get("priority",0)}]</span> <span class="badge badge-{"ok" if p.get("roi_approved") else "warn"}">{p["type"]}</span> {p.get("title","")[:45]} <span style="color:#666;float:right">{p.get("scheduled_date","")}</span></li>' for p in cal.get("planned",[])[:7]) or '<li style="color:#666">Geen items gepland</li>'}
</ul>
</div>
<div class="card">
<h3>🧠 Memory Palace</h3>
<div style="font-size:13px;color:#aaa;">
{'<br>'.join(f'💡 {m.get("insight","")[:60]}' for m in palace.get("strategic_memory",[])[-5:]) or 'Nog geen strategische inzichten'}
</div>
</div>
</div>

<button class="refresh" onclick="location.reload()">🔄 Refresh</button>

<script>
const chartDefaults = {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#888' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#666' }} }}, y: {{ ticks: {{ color: '#666' }} }} }} }};

new Chart(document.getElementById('serpChart'), {{
type: 'line',
data: {{
labels: {json.dumps(serp_dates[-14:])},
datasets: [
{{ label: 'Pagina 1', data: {json.dumps(serp_page1[-14:])}, borderColor: '#6c63ff', tension: 0.3, fill: false }},
{{ label: 'Top 3', data: {json.dumps(serp_top3[-14:])}, borderColor: '#4caf50', tension: 0.3, fill: false }}
]
}},
options: chartDefaults
}});

new Chart(document.getElementById('performersChart'), {{
type: 'bar',
data: {{
labels: {json.dumps(tp_labels)},
datasets: [{{ label: 'Score', data: {json.dumps(tp_scores)}, backgroundColor: '#6c63ff' }}]
}},
options: {{ ...chartDefaults, indexAxis: 'y' }}
}});

new Chart(document.getElementById('uptimeChart'), {{
type: 'line',
data: {{
labels: {json.dumps(uptime_times)},
datasets: [{{ label: 'Response (s)', data: {json.dumps(uptime_values)}, borderColor: '#ff9800', tension: 0.3, fill: true, backgroundColor: 'rgba(255,152,0,0.1)' }}]
}},
options: chartDefaults
}});

new Chart(document.getElementById('auditChart'), {{
type: 'line',
data: {{
labels: {json.dumps(audit_dates)},
datasets: [{{ label: 'Health Score', data: {json.dumps(audit_vals)}, borderColor: '#4caf50', tension: 0.3, fill: true, backgroundColor: 'rgba(76,175,80,0.1)' }}]
}},
options: chartDefaults
}});
</script>
</body>
</html>"""

    # Save dashboard
    dashboard_dir = f"{REPO_ROOT}/admin"
    os.makedirs(dashboard_dir, exist_ok=True)
    with open(f"{dashboard_dir}/index.html", 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

    run_command(f"cd {REPO_ROOT} && git add admin/ && git diff --cached --quiet || git commit -m 'Victor: dashboard v2 update' && git push origin main")

    return dashboard_html


# ── 14E: VICTOR MEMORY PALACE ───────────────────────────────────────────

def update_memory_palace():
    """Update het langetermijn strategisch geheugen met maand/kwartaal patronen."""
    palace = load_palace()
    today = datetime.now()
    current_month = today.strftime("%B").lower()
    current_quarter = f"Q{(today.month - 1) // 3 + 1}_{today.year}"

    # 1. Seizoenspatronen: welke content types werken deze maand
    conv = load_conversions()
    articles = conv.get("articles", {})

    if articles:
        # Groepeer per type
        type_performance = {}
        for slug, data in articles.items():
            art_type = "general"
            if 'vs' in slug: art_type = "comparison"
            elif 'alternative' in slug: art_type = "alternatives"
            elif 'pricing' in slug or 'kosten' in slug: art_type = "pricing"
            elif 'review' in slug: art_type = "review"
            elif 'how' in slug or 'tutorial' in slug: art_type = "howto"

            if art_type not in type_performance:
                type_performance[art_type] = {"total_score": 0, "count": 0, "total_clicks": 0}
            type_performance[art_type]["total_score"] += data.get("conv_score", 0)
            type_performance[art_type]["count"] += 1
            type_performance[art_type]["total_clicks"] += data.get("clicks", 0)

        # Best performing type
        best_type = max(type_performance.items(),
                       key=lambda x: x[1]["total_score"] / max(x[1]["count"], 1),
                       default=("general", {}))

        palace["seasonal_patterns"][current_month] = {
            "best_content_type": best_type[0],
            "avg_score": round(best_type[1].get("total_score", 0) / max(best_type[1].get("count", 1), 1), 1),
            "total_clicks": sum(tp.get("total_clicks", 0) for tp in type_performance.values()),
            "updated": str(today.date())
        }

    # 2. Brand trends: welke brands groeien/dalen
    serp = load_serp_data()
    tracking = serp.get("tracking", {})

    brand_perf = {}
    for brand in VAULT:
        brand_lower = brand.lower()
        brand_pages = {slug: data for slug, data in tracking.items() if brand_lower in slug}

        if brand_pages:
            avg_pos = sum(
                d["positions"][-1]["pos"]
                for d in brand_pages.values()
                if d.get("positions")
            ) / max(len(brand_pages), 1)

            rising = sum(1 for d in brand_pages.values() if d.get("trend") == "rising")
            falling = sum(1 for d in brand_pages.values() if d.get("trend") == "falling")

            trend = "growing" if rising > falling else "declining" if falling > rising else "stable"

            brand_perf[brand] = {
                "avg_position": round(avg_pos, 1),
                "pages": len(brand_pages),
                "trend": trend,
                "rising": rising,
                "falling": falling,
                "updated": str(today.date())
            }

    palace["brand_trends"] = brand_perf

    # 3. Kwartaal inzichten via Claude AI
    if articles and brand_perf:
        try:
            data_summary = f"""
Maand: {current_month}, Kwartaal: {current_quarter}
Totaal artikelen: {len(articles)}
Beste content type: {best_type[0] if articles else 'unknown'}

Brand performance:
{chr(10).join(f'  {b}: pos {d["avg_position"]}, trend {d["trend"]}' for b, d in brand_perf.items())}

Top 5 artikelen:
{chr(10).join(f'  {slug}: {data.get("conv_score",0):.0f}pts, {data.get("clicks",0)} clicks' for slug, data in sorted(articles.items(), key=lambda x: x[1].get("conv_score",0), reverse=True)[:5])}"""

            res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Je bent een strategisch SEO analist. Geef 3-5 korte strategische inzichten op basis van deze data. Focus op actiegerichte tips. Antwoord als JSON array: [{\"insight\": \"...\", \"action\": \"...\", \"priority\": \"high/medium/low\"}]"},
                    {"role": "user", "content": data_summary}
                ],
                max_tokens=800,
                temperature=0.5
            )
            result = res.choices[0].message.content.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            insights = json.loads(result)

            for ins in insights:
                ins["quarter"] = current_quarter
                ins["date"] = str(today.date())

            palace["strategic_memory"].extend(insights)
            palace["quarterly_insights"].append({
                "quarter": current_quarter,
                "insights_count": len(insights),
                "date": str(today.date())
            })

        except Exception as e:
            log(f"Memory Palace insight error: {e}")

    palace["last_update"] = str(today)
    save_palace(palace)
    return palace


def skynet_cycle():
    """Volledige Skynet Protocol cyclus."""
    actions = []

    # 1. Content Calendar update
    try:
        cal = generate_content_calendar()
        planned = cal.get("planned", [])
        actions.append(f"📋 Calendar: {len(planned)} items gepland")

        # Execute 1 item als auto_execute aan staat
        if cal.get("settings", {}).get("auto_execute"):
            result, item = execute_calendar_item()
            if result:
                actions.append(f"📝 Calendar executed: {result}")
                add_digest_item("content", f"Nieuw artikel: {result}", priority=6)
    except Exception as e:
        log(f"Calendar error: {e}")

    # 2. Memory Palace update (1x per week op zondag)
    if datetime.now().weekday() == 6:
        try:
            palace = update_memory_palace()
            insights = palace.get("strategic_memory", [])
            if insights:
                actions.append(f"🧠 Memory Palace: {len(insights)} strategische inzichten")
        except Exception as e:
            log(f"Memory Palace error: {e}")

    # 3. Dashboard v2 update
    try:
        generate_dashboard_v2()
        actions.append("📊 Dashboard v2 bijgewerkt")
    except Exception as e:
        log(f"Dashboard error: {e}")

    # 4. Outreach campaign (1x per week op woensdag)
    if datetime.now().weekday() == 2:
        try:
            results = run_outreach_campaign(max_emails=2)
            if results:
                actions.append(f"📧 Outreach: {len(results)} emails")
                for r in results:
                    add_digest_item("backlinks", r, priority=5)
        except Exception as e:
            log(f"Outreach error: {e}")

    return actions


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 15: QUANTUM CORE — Revenue Radar, Social Swarm, Predictive Engine,
#            Authority Builder, Victor Live Portal
# ══════════════════════════════════════════════════════════════════════════════

REVENUE_RADAR_FILE = "/root/felix_hq/victor_revenue_radar.json"
SOCIAL_SWARM_FILE = "/root/felix_hq/victor_social_swarm.json"
PREDICTIONS_FILE = "/root/felix_hq/victor_predictions.json"
AUTHORITY_FILE = "/root/felix_hq/victor_authority.json"
PORTAL_DIR = "/root/felix_hq/portal"

# ── 15A: REVENUE RADAR ──────────────────────────────────────────────────────

def load_revenue_radar():
    try:
        if os.path.exists(REVENUE_RADAR_FILE):
            return json.loads(open(REVENUE_RADAR_FILE).read())
    except:
        pass
    return {"tracked": {}, "forecasts": {}, "alerts": [], "optimizations": []}

def save_revenue_radar(data):
    with open(REVENUE_RADAR_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def track_revenue_per_article():
    """Track commissie-potentieel per artikel op basis van GSC clicks + affiliate links."""
    radar = load_revenue_radar()
    gsc = load_gsc_data()

    pages = gsc.get("pages", {})
    tracked = radar.get("tracked", {})

    for url, data in pages.items():
        slug = url.split("/")[-1].replace(".html", "") if "/" in url else url
        clicks = data.get("clicks", 0)
        impressions = data.get("impressions", 0)

        # Detect which brand this article promotes
        brand_match = None
        for brand in VAULT.keys():
            if brand.lower() in slug.lower():
                brand_match = brand
                break

        if brand_match:
            commission = {"Kinsta": 75, "Synthesia": 20, "InVideo": 15,
                         "Replit": 10, "Murf": 12, "Bitvavo": 5}.get(brand_match, 10)

            # Estimate monthly revenue: clicks * estimated CTR to affiliate * conversion rate
            est_affiliate_ctr = 0.12  # 12% click through to affiliate
            est_conversion = 0.03    # 3% conversion rate
            monthly_revenue = clicks * est_affiliate_ctr * est_conversion * commission

            tracked[slug] = {
                "brand": brand_match,
                "clicks": clicks,
                "impressions": impressions,
                "commission": commission,
                "est_monthly_revenue": round(monthly_revenue, 2),
                "est_yearly_revenue": round(monthly_revenue * 12, 2),
                "last_updated": datetime.now().isoformat()
            }

    radar["tracked"] = tracked
    save_revenue_radar(radar)
    return tracked

def revenue_forecast():
    """Forecast revenue trends op basis van historische data + Memory Palace seizoenspatronen."""
    radar = load_revenue_radar()
    tracked = radar.get("tracked", {})

    try:
        palace = json.loads(open(PALACE_FILE).read()) if os.path.exists(PALACE_FILE) else {}
    except:
        palace = {}

    current_month = datetime.now().strftime("%B")
    seasonal = palace.get("seasonal_patterns", {}).get(current_month, {})

    total_monthly = sum(t.get("est_monthly_revenue", 0) for t in tracked.values())
    total_yearly = sum(t.get("est_yearly_revenue", 0) for t in tracked.values())

    # Top performers
    top_articles = sorted(tracked.items(), key=lambda x: x[1].get("est_monthly_revenue", 0), reverse=True)[:5]

    # Brand breakdown
    brand_revenue = {}
    for slug, data in tracked.items():
        brand = data.get("brand", "Unknown")
        brand_revenue[brand] = brand_revenue.get(brand, 0) + data.get("est_monthly_revenue", 0)

    forecast = {
        "total_monthly": round(total_monthly, 2),
        "total_yearly": round(total_yearly, 2),
        "top_articles": [(s, d.get("est_monthly_revenue", 0)) for s, d in top_articles],
        "brand_breakdown": brand_revenue,
        "seasonal_factor": seasonal.get("multiplier", 1.0),
        "generated": datetime.now().isoformat()
    }

    radar["forecasts"] = forecast
    save_revenue_radar(radar)
    return forecast

def revenue_money_alerts():
    """Detecteer significante veranderingen in artikel performance."""
    radar = load_revenue_radar()
    tracked = radar.get("tracked", {})
    gsc = load_gsc_data()
    pages = gsc.get("pages", {})

    alerts = []
    for slug, data in tracked.items():
        prev_clicks = data.get("prev_clicks", data.get("clicks", 0))
        current_clicks = data.get("clicks", 0)

        if prev_clicks > 0:
            change_pct = ((current_clicks - prev_clicks) / prev_clicks) * 100

            if change_pct > 50:
                alerts.append({
                    "type": "spike",
                    "slug": slug,
                    "brand": data.get("brand", "?"),
                    "change": f"+{change_pct:.0f}%",
                    "revenue_impact": f"+€{data.get('est_monthly_revenue', 0) * (change_pct/100):.2f}/mo",
                    "date": datetime.now().isoformat()
                })
            elif change_pct < -30:
                alerts.append({
                    "type": "drop",
                    "slug": slug,
                    "brand": data.get("brand", "?"),
                    "change": f"{change_pct:.0f}%",
                    "revenue_impact": f"-€{abs(data.get('est_monthly_revenue', 0) * (change_pct/100)):.2f}/mo",
                    "date": datetime.now().isoformat()
                })

        # Store current as prev for next check
        data["prev_clicks"] = current_clicks

    radar["alerts"] = (radar.get("alerts", []) + alerts)[-50:]
    save_revenue_radar(radar)
    return alerts

def optimize_affiliate_links():
    """Analyseer welke affiliate placements het best converteren."""
    radar = load_revenue_radar()
    tracked = radar.get("tracked", {})

    optimizations = []
    for slug, data in tracked.items():
        clicks = data.get("clicks", 0)
        revenue = data.get("est_monthly_revenue", 0)

        # High traffic, low revenue = needs better CTA placement
        if clicks > 50 and revenue < 5:
            optimizations.append({
                "slug": slug,
                "issue": "high_traffic_low_conversion",
                "suggestion": f"Voeg prominentere CTA toe + vergelijkingstabel",
                "potential": f"+€{clicks * 0.12 * 0.05 * data.get('commission', 10):.2f}/mo"
            })

        # Low traffic, high commission = needs SEO boost
        if clicks < 20 and data.get("commission", 0) >= 50:
            optimizations.append({
                "slug": slug,
                "issue": "high_value_low_traffic",
                "suggestion": f"SEO boost nodig: meer internal links + content update",
                "potential": f"+€{50 * 0.12 * 0.03 * data.get('commission', 10):.2f}/mo bij 50 clicks"
            })

    radar["optimizations"] = optimizations
    save_revenue_radar(radar)
    return optimizations

# ── 15B: SOCIAL SWARM ───────────────────────────────────────────────────────

def load_social_swarm():
    try:
        if os.path.exists(SOCIAL_SWARM_FILE):
            return json.loads(open(SOCIAL_SWARM_FILE).read())
    except:
        pass
    return {"posts": [], "schedule": [], "engagement": {}, "repurposed": []}

def save_social_swarm(data):
    with open(SOCIAL_SWARM_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_social_posts(slug=None):
    """Genereer social media posts voor een artikel (Twitter thread + LinkedIn + Reddit)."""
    swarm = load_social_swarm()

    # Pick article to promote
    if not slug:
        # Pick highest-revenue article not recently promoted
        radar = load_revenue_radar()
        tracked = radar.get("tracked", {})
        recent_slugs = [p.get("slug") for p in swarm.get("posts", [])[-20:]]
        candidates = [(s, d) for s, d in tracked.items() if s not in recent_slugs]
        if candidates:
            candidates.sort(key=lambda x: x[1].get("est_monthly_revenue", 0), reverse=True)
            slug = candidates[0][0]

    if not slug:
        return None

    # Read article content
    article_path = os.path.join(REPO_ROOT, "b2b", f"{slug}.html")
    if not os.path.exists(article_path):
        article_path = os.path.join(REPO_ROOT, f"{slug}.html")

    article_content = ""
    if os.path.exists(article_path):
        try:
            with open(article_path) as f:
                article_content = f.read()[:3000]
        except:
            pass

    prompt = f"""Genereer social media content voor dit artikel: {slug}
URL: https://aibuildermarketplace.com/b2b/{slug}.html

Artikel excerpt: {article_content[:1500]}

Genereer exact dit format (JSON):
{{
    "twitter_thread": ["Tweet 1 (hook, max 280 chars)", "Tweet 2 (value)", "Tweet 3 (CTA met link)"],
    "linkedin_post": "LinkedIn post (professioneel, 150-200 woorden, met emoji, eindig met CTA)",
    "reddit_title": "Reddit post title (value-first, geen spam)",
    "reddit_body": "Reddit post body (helpful, niet promotional, subtiele link)",
    "hashtags": ["#tag1", "#tag2", "#tag3"]
}}

Schrijf in het Engels. Wees helpful en niet te salesy."""

    try:
        response = ask_victor(prompt, [])
        # Parse JSON from response
        json_match = response[response.find("{"):response.rfind("}")+1]
        posts_data = json.loads(json_match)
        posts_data["slug"] = slug
        posts_data["generated"] = datetime.now().isoformat()
        posts_data["status"] = "pending"

        swarm["posts"].append(posts_data)
        save_social_swarm(swarm)
        return posts_data
    except Exception as e:
        log(f"Social post generation error: {e}")
        return None

def repurpose_content(slug):
    """1 artikel → 5 content pieces: thread, post, newsletter, quote graphic text, hook."""
    prompt = f"""Repurpose dit artikel ({slug}) naar 5 content formats.
URL: https://aibuildermarketplace.com/b2b/{slug}.html

Genereer JSON:
{{
    "twitter_hook": "Killer opening tweet (max 280 chars)",
    "linkedin_carousel_slides": ["Slide 1: Hook", "Slide 2: Problem", "Slide 3: Solution", "Slide 4: Proof", "Slide 5: CTA"],
    "newsletter_snippet": "2-3 zinnen voor een newsletter (engaging, cliffhanger)",
    "quote_graphic_text": "1 krachtige quote/statistiek uit het artikel (max 15 woorden)",
    "video_script_hook": "Eerste 10 seconden van een video script (attention-grabbing)"
}}

Engels, punchy, geen fluff."""

    try:
        response = ask_victor(prompt, [])
        json_match = response[response.find("{"):response.rfind("}")+1]
        repurposed = json.loads(json_match)
        repurposed["slug"] = slug
        repurposed["date"] = datetime.now().isoformat()

        swarm = load_social_swarm()
        swarm["repurposed"].append(repurposed)
        save_social_swarm(swarm)
        return repurposed
    except Exception as e:
        log(f"Repurpose error: {e}")
        return None

def get_best_post_times():
    """Analyseer engagement data voor optimale post tijden."""
    swarm = load_social_swarm()
    engagement = swarm.get("engagement", {})

    # Default best times based on general social media research
    best_times = {
        "twitter": {"best_days": ["Tuesday", "Wednesday", "Thursday"], "best_hours": [9, 12, 17]},
        "linkedin": {"best_days": ["Tuesday", "Wednesday", "Thursday"], "best_hours": [8, 10, 12]},
        "reddit": {"best_days": ["Monday", "Wednesday", "Friday"], "best_hours": [6, 8, 13]}
    }

    # Override with actual data if available
    if engagement:
        for platform, data in engagement.items():
            if data.get("best_hour"):
                best_times[platform]["best_hours"] = [data["best_hour"]]

    return best_times

# ── 15C: PREDICTIVE ENGINE ──────────────────────────────────────────────────

def load_predictions():
    try:
        if os.path.exists(PREDICTIONS_FILE):
            return json.loads(open(PREDICTIONS_FILE).read())
    except:
        pass
    return {"seasonal_peaks": {}, "write_now_alerts": [], "competitor_gaps": [], "content_timing": []}

def save_predictions(data):
    with open(PREDICTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def analyze_seasonal_patterns():
    """Analyseer GSC data voor seizoensgebonden keyword patronen."""
    predictions = load_predictions()
    gsc = load_gsc_data()
    pages = gsc.get("pages", {})

    try:
        palace = json.loads(open(PALACE_FILE).read()) if os.path.exists(PALACE_FILE) else {}
    except:
        palace = {}

    seasonal_peaks = {}
    current_month = datetime.now().month

    # Analyze which keywords peak in which months based on impressions patterns
    for url, data in pages.items():
        slug = url.split("/")[-1].replace(".html", "") if "/" in url else url
        impressions = data.get("impressions", 0)
        clicks = data.get("clicks", 0)

        # Categorize by likely peak season
        if any(w in slug.lower() for w in ["pricing", "cost", "budget"]):
            # Budget content peaks in Q1 (planning season) and Q4 (renewal)
            peak_months = [1, 2, 10, 11]
        elif any(w in slug.lower() for w in ["alternative", "vs", "compare"]):
            # Comparison content peaks when tools renew (Q1, Q3)
            peak_months = [1, 2, 3, 7, 8, 9]
        elif any(w in slug.lower() for w in ["review", "best"]):
            # Review content peaks year-round but especially Q4
            peak_months = [9, 10, 11, 12]
        else:
            peak_months = [current_month]  # Steady traffic

        for month in peak_months:
            month_name = datetime(2024, month, 1).strftime("%B")
            if month_name not in seasonal_peaks:
                seasonal_peaks[month_name] = []
            seasonal_peaks[month_name].append({
                "slug": slug,
                "current_clicks": clicks,
                "current_impressions": impressions
            })

    predictions["seasonal_peaks"] = seasonal_peaks
    save_predictions(predictions)
    return seasonal_peaks

def generate_write_now_alerts():
    """Detecteer trending topics die NU geschreven moeten worden."""
    predictions = load_predictions()

    try:
        trends_data = json.loads(open("/root/felix_hq/victor_trends.json").read()) if os.path.exists("/root/felix_hq/victor_trends.json") else {}
    except:
        trends_data = {}

    alerts = []
    trending = trends_data.get("trending", [])

    for trend in trending[:10]:
        topic = trend.get("topic", "") if isinstance(trend, dict) else str(trend)

        # Check if we already have content for this
        existing = False
        articles_dir = os.path.join(REPO_ROOT, "b2b")
        if os.path.isdir(articles_dir):
            for f in os.listdir(articles_dir):
                if any(word in f.lower() for word in topic.lower().split()[:2]):
                    existing = True
                    break

        if not existing and topic:
            # Check relevance to our brands
            brand_match = None
            for brand in VAULT.keys():
                if brand.lower() in topic.lower():
                    brand_match = brand
                    break

            alerts.append({
                "topic": topic,
                "urgency": "HIGH" if brand_match else "MEDIUM",
                "brand": brand_match,
                "reason": f"Trending + {'direct brand match' if brand_match else 'niche relevant'}",
                "suggested_slug": topic.lower().replace(" ", "-")[:50],
                "detected": datetime.now().isoformat()
            })

    predictions["write_now_alerts"] = alerts
    save_predictions(predictions)
    return alerts

def predict_competitor_moves():
    """Voorspel welke content concurrenten gaan maken op basis van hun patronen."""
    predictions = load_predictions()

    try:
        comp_data = json.loads(open("/root/felix_hq/victor_competitors.json").read()) if os.path.exists("/root/felix_hq/victor_competitors.json") else {}
    except:
        comp_data = {}

    gaps = []
    competitors = comp_data.get("targets", [])

    for comp in competitors[:5]:
        comp_name = comp.get("name", "") if isinstance(comp, dict) else str(comp)
        comp_articles = comp.get("articles", []) if isinstance(comp, dict) else []

        # Predict based on patterns
        if comp_articles:
            recent_topics = [a.get("topic", "") for a in comp_articles[-5:] if isinstance(a, dict)]
            if recent_topics:
                gaps.append({
                    "competitor": comp_name,
                    "predicted_topics": recent_topics[:3],
                    "our_opportunity": "Write these FIRST to rank before them",
                    "confidence": "MEDIUM"
                })

    predictions["competitor_gaps"] = gaps
    save_predictions(predictions)
    return gaps

def generate_content_timing_plan():
    """Genereer optimale timing voor content publicatie."""
    predictions = load_predictions()
    seasonal = predictions.get("seasonal_peaks", {})

    current_month = datetime.now().month
    next_months = [(current_month + i - 1) % 12 + 1 for i in range(1, 4)]

    timing_plan = []
    for month_num in next_months:
        month_name = datetime(2024, month_num, 1).strftime("%B")
        peak_content = seasonal.get(month_name, [])

        if peak_content:
            timing_plan.append({
                "month": month_name,
                "write_before": datetime(2024, (month_num - 2) % 12 + 1, 15).strftime("%B 15"),
                "topics_count": len(peak_content),
                "top_topics": [p.get("slug", "?") for p in peak_content[:3]]
            })

    predictions["content_timing"] = timing_plan
    save_predictions(predictions)
    return timing_plan

# ── 15D: AUTHORITY BUILDER ──────────────────────────────────────────────────

def load_authority():
    try:
        if os.path.exists(AUTHORITY_FILE):
            return json.loads(open(AUTHORITY_FILE).read())
    except:
        pass
    return {"clusters": {}, "pillar_pages": [], "internal_links": {}, "authority_scores": {}}

def save_authority(data):
    with open(AUTHORITY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def build_topic_clusters():
    """Detecteer en bouw topic clusters uit bestaande content."""
    authority = load_authority()

    articles_dir = os.path.join(REPO_ROOT, "b2b")
    if not os.path.isdir(articles_dir):
        return {}

    files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]

    # Group articles by brand/topic
    clusters = {}
    for fname in files:
        slug = fname.replace(".html", "")

        # Detect cluster based on brand
        for brand in VAULT.keys():
            if brand.lower() in slug.lower():
                if brand not in clusters:
                    clusters[brand] = {"pillar": None, "supporting": [], "gaps": []}
                clusters[brand]["supporting"].append(slug)
                break
        else:
            # Non-brand articles - group by type
            if "vs" in slug or "alternative" in slug:
                cluster_name = "Comparisons"
            elif "pricing" in slug or "cost" in slug:
                cluster_name = "Pricing"
            elif "review" in slug or "best" in slug:
                cluster_name = "Reviews"
            else:
                cluster_name = "General"

            if cluster_name not in clusters:
                clusters[cluster_name] = {"pillar": None, "supporting": [], "gaps": []}
            clusters[cluster_name]["supporting"].append(slug)

    # Identify pillar pages (longest/most authoritative per cluster)
    for cluster_name, data in clusters.items():
        if data["supporting"]:
            # The article with most generic name is likely the pillar
            best_pillar = min(data["supporting"], key=len)
            data["pillar"] = best_pillar

            # Identify gaps
            if cluster_name in VAULT:
                expected_types = ["review", "pricing", "alternatives", "vs", "features", "tutorial"]
                existing_types = []
                for s in data["supporting"]:
                    for t in expected_types:
                        if t in s.lower():
                            existing_types.append(t)

                data["gaps"] = [t for t in expected_types if t not in existing_types]

    authority["clusters"] = clusters
    save_authority(authority)
    return clusters

def simulate_pagerank():
    """Simuleer PageRank om te bepalen welke pagina's het meeste SEO-juice doorgeven."""
    authority = load_authority()

    try:
        link_data = json.loads(open("/root/felix_hq/victor_linkgraph.json").read()) if os.path.exists("/root/felix_hq/victor_linkgraph.json") else {}
    except:
        link_data = {}

    internal_links = link_data.get("links", {})
    if not internal_links:
        # Build from filesystem
        articles_dir = os.path.join(REPO_ROOT, "b2b")
        if os.path.isdir(articles_dir):
            for fname in os.listdir(articles_dir):
                if fname.endswith('.html'):
                    slug = fname.replace(".html", "")
                    try:
                        with open(os.path.join(articles_dir, fname)) as f:
                            content = f.read()
                        # Count internal links
                        links_out = content.count('href="/b2b/') + content.count('href="../b2b/')
                        internal_links[slug] = {"outgoing": links_out}
                    except:
                        pass

    # Simple PageRank simulation
    pages = list(internal_links.keys())
    if not pages:
        return {}

    n = len(pages)
    scores = {p: 1.0 / n for p in pages}

    # Iterate PageRank
    damping = 0.85
    for _ in range(10):
        new_scores = {}
        for page in pages:
            # Base score
            rank = (1 - damping) / n
            # Add contribution from pages linking to this one
            outgoing = internal_links.get(page, {}).get("outgoing", 1)
            for other_page in pages:
                if other_page != page:
                    other_out = max(internal_links.get(other_page, {}).get("outgoing", 1), 1)
                    rank += damping * scores[other_page] / other_out / n
            new_scores[page] = rank
        scores = new_scores

    # Normalize to 0-100
    max_score = max(scores.values()) if scores else 1
    authority_scores = {p: round((s / max_score) * 100, 1) for p, s in scores.items()}

    authority["authority_scores"] = authority_scores
    authority["internal_links"] = internal_links
    save_authority(authority)
    return authority_scores

def find_link_opportunities():
    """Vind waar interne links moeten worden toegevoegd voor maximale SEO impact."""
    authority = load_authority()
    scores = authority.get("authority_scores", {})
    clusters = authority.get("clusters", {})

    opportunities = []

    # High authority pages that don't link to related content
    for cluster_name, data in clusters.items():
        pillar = data.get("pillar")
        supporting = data.get("supporting", [])

        if pillar and len(supporting) > 1:
            pillar_score = scores.get(pillar, 0)
            for article in supporting:
                if article != pillar:
                    article_score = scores.get(article, 0)
                    if article_score < pillar_score * 0.5:
                        opportunities.append({
                            "from": pillar,
                            "to": article,
                            "reason": f"Pillar ({pillar_score:.0f}) → Supporting ({article_score:.0f})",
                            "impact": "HIGH"
                        })

    return opportunities[:20]

def calculate_cluster_authority():
    """Bereken authority score per topic cluster."""
    authority = load_authority()
    clusters = authority.get("clusters", {})
    scores = authority.get("authority_scores", {})
    gsc = load_gsc_data()
    pages = gsc.get("pages", {})

    cluster_scores = {}
    for cluster_name, data in clusters.items():
        supporting = data.get("supporting", [])
        if not supporting:
            continue

        # Average PageRank score
        avg_pr = sum(scores.get(s, 0) for s in supporting) / len(supporting)

        # Total traffic
        total_clicks = 0
        for s in supporting:
            for url, pdata in pages.items():
                if s in url:
                    total_clicks += pdata.get("clicks", 0)

        # Completeness (fewer gaps = higher score)
        gaps = len(data.get("gaps", []))
        completeness = max(0, 100 - gaps * 15)

        cluster_scores[cluster_name] = {
            "authority_score": round((avg_pr * 0.4 + completeness * 0.3 + min(total_clicks, 100) * 0.3), 1),
            "articles": len(supporting),
            "avg_pagerank": round(avg_pr, 1),
            "total_clicks": total_clicks,
            "completeness": completeness,
            "gaps": data.get("gaps", [])
        }

    authority["cluster_scores"] = cluster_scores
    save_authority(authority)
    return cluster_scores

# ── 15E: VICTOR LIVE PORTAL ─────────────────────────────────────────────────

def generate_live_portal():
    """Genereer een real-time web portal met alle Victor data."""
    os.makedirs(PORTAL_DIR, exist_ok=True)

    # Collect all data
    radar = load_revenue_radar()
    authority = load_authority()
    predictions = load_predictions()
    swarm = load_social_swarm()
    gsc = load_gsc_data()

    forecast = radar.get("forecasts", {})
    cluster_scores = authority.get("cluster_scores", {})
    alerts = radar.get("alerts", [])[-10:]

    # Generate portal HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Victor 17.0 Omega Core — Live Portal</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0a0a0f; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; padding: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; }}
        .card {{ background: #1a1a2e; border-radius: 12px; padding: 24px; border: 1px solid #2a2a4a; }}
        .card h2 {{ color: #00d4ff; margin-bottom: 16px; font-size: 1.1rem; }}
        .metric {{ font-size: 2rem; font-weight: bold; color: #fff; }}
        .metric-label {{ color: #888; font-size: 0.85rem; margin-top: 4px; }}
        .alert {{ padding: 8px 12px; margin: 4px 0; border-radius: 6px; font-size: 0.85rem; }}
        .alert-spike {{ background: #1a3a1a; border-left: 3px solid #00ff88; }}
        .alert-drop {{ background: #3a1a1a; border-left: 3px solid #ff4444; }}
        .bar {{ height: 8px; border-radius: 4px; margin: 4px 0; }}
        .progress {{ display: flex; align-items: center; margin: 8px 0; }}
        .progress-label {{ width: 100px; font-size: 0.8rem; color: #aaa; }}
        .progress-bar {{ flex: 1; height: 6px; background: #2a2a4a; border-radius: 3px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #00d4ff, #7b2ff7); border-radius: 3px; }}
        header {{ text-align: center; margin-bottom: 30px; }}
        header h1 {{ font-size: 1.8rem; background: linear-gradient(90deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        header p {{ color: #666; margin-top: 8px; }}
        .ticker {{ background: #111; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; overflow: hidden; }}
        .ticker span {{ color: #00ff88; font-weight: bold; margin: 0 20px; }}
        canvas {{ max-height: 200px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #2a2a4a; }}
        th {{ color: #00d4ff; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }}
        .badge-high {{ background: #1a3a1a; color: #00ff88; }}
        .badge-med {{ background: #3a3a1a; color: #ffaa00; }}
        @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <header>
        <h1>Victor 17.0 Omega Core</h1>
        <p>Live Portal — Updated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
    </header>

    <div class="ticker">
        <span>💰 €{forecast.get('total_monthly', 0):.2f}/mo</span>
        <span>📈 €{forecast.get('total_yearly', 0):.2f}/yr</span>
        <span>📊 {len(gsc.get('pages', {}))} pages tracked</span>
        <span>🏗️ {sum(len(c.get('supporting', [])) for c in authority.get('clusters', {}).values())} articles</span>
    </div>

    <div class="grid">
        <div class="card">
            <h2>💰 Revenue Radar</h2>
            <div class="metric">€{forecast.get('total_monthly', 0):.2f}</div>
            <div class="metric-label">Estimated Monthly Revenue</div>
            <canvas id="revenueChart"></canvas>
        </div>

        <div class="card">
            <h2>🚨 Money Alerts</h2>
            {''.join(f'<div class="alert alert-{a.get("type", "spike")}">{"📈" if a.get("type") == "spike" else "📉"} {a.get("slug", "?")[:30]} — {a.get("change", "?")} ({a.get("revenue_impact", "?")})</div>' for a in alerts[-5:])}
            {('<div style="color:#666;margin-top:10px;">Geen recente alerts</div>' if not alerts else '')}
        </div>

        <div class="card">
            <h2>🏛️ Authority Clusters</h2>
            {''.join(f'<div class="progress"><span class="progress-label">{name[:12]}</span><div class="progress-bar"><div class="progress-fill" style="width:{data.get("authority_score", 0)}%"></div></div><span style="margin-left:8px;font-size:0.8rem;">{data.get("authority_score", 0)}</span></div>' for name, data in list(cluster_scores.items())[:8])}
        </div>

        <div class="card">
            <h2>🔮 Predictions</h2>
            <table>
                <tr><th>Alert</th><th>Topic</th><th>Urgency</th></tr>
                {''.join(f'<tr><td>⚡</td><td>{a.get("topic", "?")[:35]}</td><td><span class="badge badge-{"high" if a.get("urgency") == "HIGH" else "med"}">{a.get("urgency", "?")}</span></td></tr>' for a in predictions.get("write_now_alerts", [])[:5])}
            </table>
        </div>

        <div class="card">
            <h2>📱 Social Swarm</h2>
            <div class="metric">{len(swarm.get('posts', []))}</div>
            <div class="metric-label">Posts Generated</div>
            <div style="margin-top:12px;color:#888;">
                Repurposed: {len(swarm.get('repurposed', []))} articles<br>
                Scheduled: {len(swarm.get('schedule', []))} posts
            </div>
        </div>

        <div class="card">
            <h2>📊 Brand Revenue Breakdown</h2>
            <canvas id="brandChart"></canvas>
        </div>
    </div>

    <script>
        // Revenue by brand chart
        const brandData = {json.dumps(forecast.get('brand_breakdown', {}))};
        new Chart(document.getElementById('brandChart'), {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(brandData),
                datasets: [{{ data: Object.values(brandData), backgroundColor: ['#00d4ff', '#7b2ff7', '#00ff88', '#ff6b6b', '#ffa500', '#ff69b4'] }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#aaa' }} }} }} }}
        }});

        // Revenue trend (mock with top articles)
        const topArticles = {json.dumps([a[0][:15] for a in forecast.get('top_articles', [])])};
        const topRevenue = {json.dumps([a[1] for a in forecast.get('top_articles', [])])};
        new Chart(document.getElementById('revenueChart'), {{
            type: 'bar',
            data: {{
                labels: topArticles,
                datasets: [{{ label: '€/month', data: topRevenue, backgroundColor: '#7b2ff7' }}]
            }},
            options: {{ responsive: true, scales: {{ y: {{ ticks: {{ color: '#888' }} }}, x: {{ ticks: {{ color: '#888' }} }} }}, plugins: {{ legend: {{ display: false }} }} }}
        }});
    </script>
</body>
</html>"""

    portal_path = os.path.join(PORTAL_DIR, "index.html")
    with open(portal_path, 'w') as f:
        f.write(html)

    log(f"Live portal generated: {portal_path}")
    return portal_path

# ── 15F: QUANTUM CORE ORCHESTRATOR ─────────────────────────────────────────

def quantum_cycle():
    """Volledige Quantum Core cyclus: revenue + predictions + authority + social + portal."""
    actions = []

    # Revenue Radar
    try:
        tracked = track_revenue_per_article()
        if tracked:
            actions.append(f"💰 Revenue: {len(tracked)} artikelen getracked")
        forecast = revenue_forecast()
        if forecast:
            actions.append(f"📊 Forecast: €{forecast.get('total_monthly', 0):.2f}/maand geschat")
        alerts = revenue_money_alerts()
        if alerts:
            actions.append(f"🚨 {len(alerts)} money alerts gedetecteerd")
            for alert in alerts[:3]:
                if alert.get("type") == "spike":
                    bot.send_message(ADMIN_ID, f"💰 MONEY ALERT: {alert['slug']} {alert['change']} — {alert['revenue_impact']}")
        optimizations = optimize_affiliate_links()
        if optimizations:
            actions.append(f"🔧 {len(optimizations)} affiliate optimalisaties gevonden")
    except Exception as e:
        log(f"Revenue radar error: {e}")

    # Predictive Engine
    try:
        seasonal = analyze_seasonal_patterns()
        if seasonal:
            actions.append(f"📅 Seizoensanalyse: {len(seasonal)} maanden geanalyseerd")
        write_alerts = generate_write_now_alerts()
        if write_alerts:
            actions.append(f"⚡ {len(write_alerts)} write-now alerts")
            for wa in write_alerts[:2]:
                if wa.get("urgency") == "HIGH":
                    add_digest_item("predictions", f"WRITE NOW: {wa['topic']} ({wa['brand']})", priority=9)
        timing = generate_content_timing_plan()
        if timing:
            actions.append(f"🗓️ Content timing: {len(timing)} maanden gepland")
    except Exception as e:
        log(f"Predictive engine error: {e}")

    # Authority Builder
    try:
        clusters = build_topic_clusters()
        if clusters:
            actions.append(f"🏛️ {len(clusters)} topic clusters geïdentificeerd")
        pagerank = simulate_pagerank()
        if pagerank:
            actions.append(f"📊 PageRank: {len(pagerank)} pagina's gescoord")
        cluster_auth = calculate_cluster_authority()
        if cluster_auth:
            top_cluster = max(cluster_auth.items(), key=lambda x: x[1].get("authority_score", 0))
            actions.append(f"👑 Top cluster: {top_cluster[0]} (score: {top_cluster[1].get('authority_score', 0)})")
        link_opps = find_link_opportunities()
        if link_opps:
            actions.append(f"🔗 {len(link_opps)} link opportunities gevonden")
    except Exception as e:
        log(f"Authority builder error: {e}")

    # Social Swarm (generate 1 post per cycle)
    try:
        post = generate_social_posts()
        if post:
            actions.append(f"📱 Social post gegenereerd voor: {post.get('slug', '?')}")
    except Exception as e:
        log(f"Social swarm error: {e}")

    # Live Portal
    try:
        portal_path = generate_live_portal()
        if portal_path:
            actions.append(f"🌐 Live portal updated: {portal_path}")
    except Exception as e:
        log(f"Portal error: {e}")

    return actions


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 16: OMEGA PROTOCOL — Auto-Monetize, Content Fortress, Viral Loops,
#            Self-Evolution, War Room
# ══════════════════════════════════════════════════════════════════════════════

MONETIZE_FILE = "/root/felix_hq/victor_monetize.json"
FORTRESS_FILE = "/root/felix_hq/victor_fortress.json"
VIRAL_FILE = "/root/felix_hq/victor_viral.json"
EVOLUTION_FILE = "/root/felix_hq/victor_evolution.json"
WARROOM_FILE = "/root/felix_hq/victor_warroom.json"

# ── 16A: AUTO-MONETIZE ENGINE ───────────────────────────────────────────────

def load_monetize():
    try:
        if os.path.exists(MONETIZE_FILE):
            return json.loads(open(MONETIZE_FILE).read())
    except:
        pass
    return {"scans": [], "injections": [], "cta_tests": {}, "commission_optimizer": {}}

def save_monetize(data):
    with open(MONETIZE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def scan_missed_affiliate_opportunities():
    """Scan alle artikelen op gemiste affiliate kansen."""
    monetize = load_monetize()
    articles_dir = os.path.join(REPO_ROOT, "b2b")
    if not os.path.isdir(articles_dir):
        return []

    opportunities = []
    brand_keywords = {
        "Kinsta": ["kinsta", "hosting", "wordpress hosting", "managed hosting"],
        "Synthesia": ["synthesia", "ai video", "video generator", "avatar video"],
        "InVideo": ["invideo", "video editor", "video maker", "online video"],
        "Replit": ["replit", "online ide", "code editor", "coding platform"],
        "Murf": ["murf", "ai voice", "voiceover", "text to speech"],
        "Bitvavo": ["bitvavo", "crypto", "bitcoin", "exchange"]
    }

    for fname in os.listdir(articles_dir):
        if not fname.endswith('.html'):
            continue
        slug = fname.replace(".html", "")

        try:
            with open(os.path.join(articles_dir, fname)) as f:
                content = f.read().lower()
        except:
            continue

        for brand, keywords in brand_keywords.items():
            affiliate_url = VAULT.get(brand, "")
            # Check if brand is mentioned but affiliate link is missing
            brand_mentioned = any(kw in content for kw in keywords)
            has_affiliate = affiliate_url.lower() in content if affiliate_url else False

            if brand_mentioned and not has_affiliate and brand.lower() not in slug.lower():
                mention_count = sum(content.count(kw) for kw in keywords)
                if mention_count >= 2:
                    opportunities.append({
                        "slug": slug,
                        "brand": brand,
                        "mentions": mention_count,
                        "affiliate_url": affiliate_url,
                        "potential_revenue": mention_count * 0.5,  # rough estimate
                        "action": f"Add {brand} affiliate link ({mention_count} mentions without link)"
                    })

    monetize["scans"] = opportunities
    monetize["last_scan"] = datetime.now().isoformat()
    save_monetize(monetize)
    return opportunities

def inject_affiliate_links(slug=None, dry_run=True):
    """Voeg affiliate links toe op logische plekken in artikelen."""
    opportunities = scan_missed_affiliate_opportunities()
    if slug:
        opportunities = [o for o in opportunities if o["slug"] == slug]

    injections = []
    for opp in opportunities[:5]:
        article_path = os.path.join(REPO_ROOT, "b2b", f"{opp['slug']}.html")
        if not os.path.exists(article_path):
            continue

        try:
            with open(article_path) as f:
                content = f.read()
        except:
            continue

        brand = opp["brand"]
        affiliate_url = opp["affiliate_url"]

        if not dry_run and affiliate_url:
            # Find first mention of brand without a link and wrap it
            import re
            # Simple injection: find brand name not already in a link
            pattern = rf'(?<!href="[^"]*?)(?<!>)({re.escape(brand)})(?!</a>)'
            replacement = f'<a href="{affiliate_url}" target="_blank" rel="nofollow sponsored">{brand}</a>'

            new_content, count = re.subn(pattern, replacement, content, count=1)
            if count > 0:
                with open(article_path, 'w') as f:
                    f.write(new_content)
                injections.append({
                    "slug": opp["slug"],
                    "brand": brand,
                    "action": "injected",
                    "date": datetime.now().isoformat()
                })
        else:
            injections.append({
                "slug": opp["slug"],
                "brand": brand,
                "action": "dry_run",
                "suggestion": f"Add link to {brand} ({opp['mentions']} mentions)"
            })

    monetize = load_monetize()
    monetize["injections"] = (monetize.get("injections", []) + injections)[-100:]
    save_monetize(monetize)
    return injections

def optimize_commissions():
    """Analyseer welke brands het best converteren en optimaliseer focus."""
    radar = load_revenue_radar()
    tracked = radar.get("tracked", {})

    brand_performance = {}
    for slug, data in tracked.items():
        brand = data.get("brand")
        if brand:
            if brand not in brand_performance:
                brand_performance[brand] = {"articles": 0, "total_clicks": 0, "total_revenue": 0, "commission": data.get("commission", 0)}
            brand_performance[brand]["articles"] += 1
            brand_performance[brand]["total_clicks"] += data.get("clicks", 0)
            brand_performance[brand]["total_revenue"] += data.get("est_monthly_revenue", 0)

    # Calculate efficiency: revenue per article
    for brand, perf in brand_performance.items():
        perf["revenue_per_article"] = perf["total_revenue"] / max(perf["articles"], 1)
        perf["clicks_per_article"] = perf["total_clicks"] / max(perf["articles"], 1)
        perf["efficiency_score"] = (perf["revenue_per_article"] * 0.6 + perf["clicks_per_article"] * 0.4)

    # Recommendations
    sorted_brands = sorted(brand_performance.items(), key=lambda x: x[1]["efficiency_score"], reverse=True)

    recommendations = []
    for brand, perf in sorted_brands:
        if perf["efficiency_score"] > 5:
            recommendations.append(f"📈 MEER {brand} content — €{perf['revenue_per_article']:.2f}/artikel, top performer")
        elif perf["efficiency_score"] < 1 and perf["articles"] > 3:
            recommendations.append(f"📉 MINDER {brand} — lage conversie ondanks {perf['articles']} artikelen")

    monetize = load_monetize()
    monetize["commission_optimizer"] = {"brands": brand_performance, "recommendations": recommendations, "date": datetime.now().isoformat()}
    save_monetize(monetize)
    return {"brands": brand_performance, "recommendations": recommendations}

# ── 16B: CONTENT FORTRESS (E-E-A-T) ────────────────────────────────────────

def load_fortress():
    try:
        if os.path.exists(FORTRESS_FILE):
            return json.loads(open(FORTRESS_FILE).read())
    except:
        pass
    return {"eeat_scores": {}, "trust_signals": [], "fact_checks": [], "experience_markers": []}

def save_fortress(data):
    with open(FORTRESS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def score_eeat(slug=None):
    """Score artikelen op E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)."""
    fortress = load_fortress()
    articles_dir = os.path.join(REPO_ROOT, "b2b")
    if not os.path.isdir(articles_dir):
        return {}

    files = [f"{slug}.html"] if slug else [f for f in os.listdir(articles_dir) if f.endswith('.html')]
    eeat_scores = fortress.get("eeat_scores", {})

    for fname in files[:20]:
        article_slug = fname.replace(".html", "")
        try:
            with open(os.path.join(articles_dir, fname)) as f:
                content = f.read().lower()
        except:
            continue

        # Experience signals
        experience_keywords = ["i tested", "i tried", "in my experience", "after using", "i've been using",
                             "hands-on", "my review", "i found that", "when i", "personally"]
        experience_score = min(sum(1 for kw in experience_keywords if kw in content) * 15, 100)

        # Expertise signals
        expertise_keywords = ["according to", "research shows", "data indicates", "study found",
                            "statistics", "benchmark", "compared to", "analysis", "methodology"]
        expertise_score = min(sum(1 for kw in expertise_keywords if kw in content) * 12, 100)

        # Authority signals
        authority_signals = ["author" in content, "about" in content and "years" in content,
                           "expert" in content, "certified" in content, "published" in content]
        authority_score = min(sum(1 for s in authority_signals if s) * 20, 100)

        # Trust signals
        trust_keywords = ["updated" in content, "last modified" in content, "verified" in content,
                        "source:" in content or "sources:" in content, "disclaimer" in content,
                        "affiliate" in content and "disclosure" in content]
        trust_score = min(sum(1 for s in trust_keywords if s) * 18, 100)

        overall = (experience_score * 0.3 + expertise_score * 0.25 + authority_score * 0.2 + trust_score * 0.25)

        eeat_scores[article_slug] = {
            "experience": experience_score,
            "expertise": expertise_score,
            "authority": authority_score,
            "trust": trust_score,
            "overall": round(overall, 1),
            "grade": "A" if overall >= 80 else "B" if overall >= 60 else "C" if overall >= 40 else "D",
            "scanned": datetime.now().isoformat()
        }

    fortress["eeat_scores"] = eeat_scores
    save_fortress(fortress)
    return eeat_scores

def generate_trust_signals(slug):
    """Genereer trust signals die aan een artikel moeten worden toegevoegd."""
    fortress = load_fortress()
    eeat = fortress.get("eeat_scores", {}).get(slug, {})

    suggestions = []

    if eeat.get("experience", 0) < 50:
        suggestions.append({
            "type": "experience",
            "action": "Add first-person experience paragraph",
            "example": "After testing [tool] for 3 months on our own projects, here's what we found...",
            "impact": "HIGH"
        })

    if eeat.get("trust", 0) < 50:
        suggestions.append({
            "type": "trust",
            "action": "Add update date + affiliate disclosure",
            "example": "Last updated: [date] | This article contains affiliate links (full disclosure)",
            "impact": "HIGH"
        })

    if eeat.get("expertise", 0) < 50:
        suggestions.append({
            "type": "expertise",
            "action": "Add data/statistics + methodology",
            "example": "Based on our analysis of [X] tools across [Y] criteria...",
            "impact": "MEDIUM"
        })

    if eeat.get("authority", 0) < 50:
        suggestions.append({
            "type": "authority",
            "action": "Add author bio + credentials",
            "example": "Written by [name], who has [X] years experience with AI tools",
            "impact": "MEDIUM"
        })

    fortress["trust_signals"] = suggestions
    save_fortress(fortress)
    return suggestions

def fact_check_articles():
    """Detecteer verouderde claims in artikelen."""
    fortress = load_fortress()
    articles_dir = os.path.join(REPO_ROOT, "b2b")
    if not os.path.isdir(articles_dir):
        return []

    outdated = []
    current_year = datetime.now().year

    for fname in os.listdir(articles_dir):
        if not fname.endswith('.html'):
            continue
        slug = fname.replace(".html", "")

        try:
            with open(os.path.join(articles_dir, fname)) as f:
                content = f.read()
        except:
            continue

        # Check for outdated year references
        for year in range(2020, current_year - 1):
            if str(year) in content and f"founded in {year}" not in content.lower():
                outdated.append({
                    "slug": slug,
                    "issue": f"Contains reference to {year} — may be outdated",
                    "severity": "HIGH" if year < current_year - 2 else "MEDIUM"
                })
                break

        # Check for outdated pricing claims
        if "pricing" in slug.lower() or "cost" in slug.lower():
            # Pricing articles older than 3 months need refresh
            try:
                mtime = os.path.getmtime(os.path.join(articles_dir, fname))
                age_days = (datetime.now() - datetime.fromtimestamp(mtime)).days
                if age_days > 90:
                    outdated.append({
                        "slug": slug,
                        "issue": f"Pricing article is {age_days} days old — needs refresh",
                        "severity": "HIGH"
                    })
            except:
                pass

    fortress["fact_checks"] = outdated
    save_fortress(fortress)
    return outdated

# ── 16C: VIRAL LOOP GENERATOR ──────────────────────────────────────────────

def load_viral():
    try:
        if os.path.exists(VIRAL_FILE):
            return json.loads(open(VIRAL_FILE).read())
    except:
        pass
    return {"tables": [], "stat_cards": [], "link_magnets": [], "embeddables": []}

def save_viral(data):
    with open(VIRAL_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_comparison_table(brands=None):
    """Genereer een embeddable vergelijkingstabel met affiliate links."""
    if not brands:
        brands = list(VAULT.keys())

    prompt = f"""Maak een HTML vergelijkingstabel voor deze AI tools: {', '.join(brands)}

De tabel moet bevatten:
- Tool naam (met affiliate link)
- Prijs (starting price)
- Beste voor (1 zin)
- Score (uit 5 sterren)
- Uniek voordeel

Format: pure HTML tabel, dark theme (background #1a1a2e, text #e0e0e0, header #00d4ff).
Affiliate URLs: {json.dumps({b: VAULT[b] for b in brands if b in VAULT})}

Maak het compact, visueel aantrekkelijk, mobile-friendly. Voeg rel="nofollow sponsored" toe aan affiliate links."""

    try:
        response = ask_victor(prompt, [])
        table_html = response[response.find("<"):response.rfind(">")+1] if "<" in response else response

        viral = load_viral()
        viral["tables"].append({
            "brands": brands,
            "html": table_html,
            "generated": datetime.now().isoformat()
        })
        save_viral(viral)
        return table_html
    except Exception as e:
        log(f"Comparison table error: {e}")
        return None

def generate_stat_cards(slug):
    """Genereer shareable stat cards/quotes uit een artikel."""
    article_path = os.path.join(REPO_ROOT, "b2b", f"{slug}.html")
    if not os.path.exists(article_path):
        return []

    try:
        with open(article_path) as f:
            content = f.read()[:3000]
    except:
        return []

    prompt = f"""Uit dit artikel ({slug}), genereer 3 "stat cards" — korte, shareable quotes/statistieken.

Artikel: {content[:2000]}

Format (JSON array):
[
    {{"text": "Korte impactvolle stat of quote (max 20 woorden)", "type": "statistic|quote|insight", "visual_suggestion": "achtergrond kleur/style suggestie"}},
    ...
]

Maak ze punchy, deelbaar op social media, en relevant voor AI/tech professionals."""

    try:
        response = ask_victor(prompt, [])
        json_match = response[response.find("["):response.rfind("]")+1]
        cards = json.loads(json_match)

        viral = load_viral()
        viral["stat_cards"].append({"slug": slug, "cards": cards, "date": datetime.now().isoformat()})
        save_viral(viral)
        return cards
    except Exception as e:
        log(f"Stat cards error: {e}")
        return []

def generate_link_magnet_ideas():
    """Genereer ideeën voor gratis tools/calculators die backlinks trekken."""
    prompt = """Genereer 5 ideeën voor gratis online tools/calculators die relevant zijn voor AI Builder Marketplace
(een site die AI tools vergelijkt voor bedrijven: video AI, hosting, crypto, voice AI, coding).

Elke tool moet:
1. Makkelijk te bouwen zijn (1 HTML pagina met JS)
2. Waarde bieden die mensen willen linken/delen
3. Subtiel naar affiliate content verwijzen

Format (JSON):
[
    {"name": "Tool naam", "description": "Wat het doet", "seo_value": "Welke keywords het target", "build_complexity": "LOW|MEDIUM", "backlink_potential": "HIGH|MEDIUM"},
    ...
]"""

    try:
        response = ask_victor(prompt, [])
        json_match = response[response.find("["):response.rfind("]")+1]
        magnets = json.loads(json_match)

        viral = load_viral()
        viral["link_magnets"] = magnets
        save_viral(viral)
        return magnets
    except Exception as e:
        log(f"Link magnet ideas error: {e}")
        return []

# ── 16D: SELF-EVOLUTION CORE ───────────────────────────────────────────────

def load_evolution():
    try:
        if os.path.exists(EVOLUTION_FILE):
            return json.loads(open(EVOLUTION_FILE).read())
    except:
        pass
    return {"performance_log": [], "tuning_history": [], "proposals": [], "weekly_journal": []}

def save_evolution(data):
    with open(EVOLUTION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def analyze_cycle_performance():
    """Analyseer welke Victor cycles het meeste opleveren."""
    evolution = load_evolution()

    # Read log file for cycle timing/results
    log_data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                lines = f.readlines()[-500:]
            for line in lines:
                if "cycle done" in line.lower() or "error" in line.lower():
                    log_data.append(line.strip())
        except:
            pass

    # Analyze which modules produce results
    module_performance = {
        "domination": {"runs": 0, "errors": 0, "actions": 0},
        "skynet": {"runs": 0, "errors": 0, "actions": 0},
        "quantum": {"runs": 0, "errors": 0, "actions": 0},
        "omniscience": {"runs": 0, "errors": 0, "actions": 0},
        "neural": {"runs": 0, "errors": 0, "actions": 0},
    }

    for line in log_data:
        for module in module_performance:
            if module in line.lower():
                if "error" in line.lower():
                    module_performance[module]["errors"] += 1
                elif "done" in line.lower():
                    module_performance[module]["runs"] += 1
                    # Extract action count if present
                    import re
                    match = re.search(r'(\d+)\s*actions', line)
                    if match:
                        module_performance[module]["actions"] += int(match.group(1))

    # Calculate efficiency
    for module, perf in module_performance.items():
        perf["efficiency"] = perf["actions"] / max(perf["runs"], 1)
        perf["error_rate"] = perf["errors"] / max(perf["runs"] + perf["errors"], 1) * 100

    evolution["performance_log"].append({
        "date": datetime.now().isoformat(),
        "modules": module_performance
    })
    # Keep last 30 entries
    evolution["performance_log"] = evolution["performance_log"][-30:]
    save_evolution(evolution)
    return module_performance

def auto_tune_parameters():
    """Auto-tune Victor's parameters op basis van resultaten."""
    evolution = load_evolution()
    perf_log = evolution.get("performance_log", [])

    tunings = []

    if len(perf_log) >= 3:
        # Check recent error rates
        recent = perf_log[-3:]
        for module_name in ["domination", "skynet", "quantum", "omniscience"]:
            avg_errors = sum(p["modules"].get(module_name, {}).get("error_rate", 0) for p in recent) / 3
            if avg_errors > 50:
                tunings.append({
                    "module": module_name,
                    "issue": f"High error rate ({avg_errors:.0f}%)",
                    "suggestion": f"Reduce frequency or add more error handling for {module_name}",
                    "auto_action": "reduce_frequency"
                })

            avg_efficiency = sum(p["modules"].get(module_name, {}).get("efficiency", 0) for p in recent) / 3
            if avg_efficiency < 1 and module_name != "quantum":
                tunings.append({
                    "module": module_name,
                    "issue": f"Low efficiency ({avg_efficiency:.1f} actions/run)",
                    "suggestion": f"Module {module_name} produces few results — consider optimizing triggers",
                    "auto_action": "optimize"
                })

    evolution["tuning_history"].append({
        "date": datetime.now().isoformat(),
        "tunings": tunings
    })
    save_evolution(evolution)
    return tunings

def generate_improvement_proposals():
    """Victor genereert zelf verbetervoorstellen."""
    evolution = load_evolution()
    perf_log = evolution.get("performance_log", [])
    tunings = evolution.get("tuning_history", [])

    # Gather context
    radar = load_revenue_radar()
    forecast = radar.get("forecasts", {})

    prompt = f"""Je bent Victor, een AI SEO agent. Analyseer je eigen prestaties en genereer 3 concrete verbetervoorstellen.

Performance data:
- Revenue forecast: €{forecast.get('total_monthly', 0):.2f}/maand
- Recent tunings: {json.dumps(tunings[-3:]) if tunings else 'geen'}
- Module performance: {json.dumps(perf_log[-1]['modules']) if perf_log else 'geen data'}

Genereer JSON met 3 voorstellen:
[
    {{"title": "Voorstel titel", "problem": "Wat gaat er mis/suboptimaal", "solution": "Concrete oplossing", "expected_impact": "Verwacht resultaat", "priority": "HIGH|MEDIUM|LOW"}},
    ...
]

Focus op: meer revenue, betere rankings, efficiëntere cycles."""

    try:
        response = ask_victor(prompt, [])
        json_match = response[response.find("["):response.rfind("]")+1]
        proposals = json.loads(json_match)

        evolution["proposals"] = proposals
        evolution["proposals_date"] = datetime.now().isoformat()
        save_evolution(evolution)
        return proposals
    except Exception as e:
        log(f"Improvement proposals error: {e}")
        return []

def write_weekly_journal():
    """Victor schrijft een wekelijks performance journal."""
    evolution = load_evolution()
    radar = load_revenue_radar()
    authority = load_authority()

    forecast = radar.get("forecasts", {})
    cluster_scores = authority.get("cluster_scores", {})

    journal_entry = {
        "week": datetime.now().strftime("%Y-W%V"),
        "date": datetime.now().isoformat(),
        "metrics": {
            "est_monthly_revenue": forecast.get("total_monthly", 0),
            "articles_tracked": len(radar.get("tracked", {})),
            "clusters": len(cluster_scores),
            "top_cluster_score": max((c.get("authority_score", 0) for c in cluster_scores.values()), default=0)
        },
        "highlights": [],
        "lowlights": [],
        "next_week_focus": []
    }

    # Auto-detect highlights
    if forecast.get("total_monthly", 0) > 50:
        journal_entry["highlights"].append(f"Revenue boven €50/maand target")
    alerts = radar.get("alerts", [])
    spikes = [a for a in alerts if a.get("type") == "spike"]
    if spikes:
        journal_entry["highlights"].append(f"{len(spikes)} traffic spikes gedetecteerd")

    # Auto-detect lowlights
    drops = [a for a in alerts if a.get("type") == "drop"]
    if drops:
        journal_entry["lowlights"].append(f"{len(drops)} traffic drops — actie nodig")

    evolution["weekly_journal"].append(journal_entry)
    evolution["weekly_journal"] = evolution["weekly_journal"][-52:]  # Keep 1 year
    save_evolution(evolution)
    return journal_entry

# ── 16E: WAR ROOM ──────────────────────────────────────────────────────────

def load_warroom():
    try:
        if os.path.exists(WARROOM_FILE):
            return json.loads(open(WARROOM_FILE).read())
    except:
        pass
    return {"battles": [], "velocity": {}, "victories": [], "counter_plans": []}

def save_warroom(data):
    with open(WARROOM_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def detect_ranking_battles():
    """Detecteer wanneer concurrenten ons inhalen op keywords."""
    warroom = load_warroom()
    gsc = load_gsc_data()
    serp_data = {}

    try:
        serp_file = "/root/felix_hq/victor_serp.json"
        if os.path.exists(serp_file):
            serp_data = json.loads(open(serp_file).read())
    except:
        pass

    battles = []
    positions = serp_data.get("positions", {})

    for keyword, pos_data in positions.items():
        current_pos = pos_data.get("position", 0)
        prev_pos = pos_data.get("prev_position", current_pos)

        if current_pos > prev_pos and prev_pos > 0:
            # We dropped — competitor may have overtaken us
            drop = current_pos - prev_pos
            if drop >= 3:
                battles.append({
                    "keyword": keyword,
                    "prev_position": prev_pos,
                    "current_position": current_pos,
                    "drop": drop,
                    "severity": "CRITICAL" if drop >= 5 else "WARNING",
                    "detected": datetime.now().isoformat(),
                    "action_needed": True
                })

        # Update prev for next check
        pos_data["prev_position"] = current_pos

    # Check for victories (reaching #1-3)
    victories = []
    for keyword, pos_data in positions.items():
        current_pos = pos_data.get("position", 0)
        if 1 <= current_pos <= 3:
            victories.append({
                "keyword": keyword,
                "position": current_pos,
                "detected": datetime.now().isoformat()
            })

    warroom["battles"] = (warroom.get("battles", []) + battles)[-50:]
    warroom["victories"] = (warroom.get("victories", []) + victories)[-50:]

    # Save SERP data back
    try:
        with open("/root/felix_hq/victor_serp.json", 'w') as f:
            json.dump(serp_data, f, indent=2)
    except:
        pass

    save_warroom(warroom)
    return battles, victories

def calculate_ranking_velocity():
    """Bereken hoe snel keywords stijgen/dalen."""
    warroom = load_warroom()
    serp_data = {}

    try:
        serp_file = "/root/felix_hq/victor_serp.json"
        if os.path.exists(serp_file):
            serp_data = json.loads(open(serp_file).read())
    except:
        pass

    velocity = {}
    positions = serp_data.get("positions", {})
    history = serp_data.get("history", {})

    for keyword, pos_data in positions.items():
        current_pos = pos_data.get("position", 0)
        keyword_history = history.get(keyword, [])

        if len(keyword_history) >= 2:
            # Calculate velocity (positions gained per week)
            oldest = keyword_history[0].get("position", current_pos) if keyword_history else current_pos
            weeks = max(len(keyword_history) / 7, 1)
            vel = (oldest - current_pos) / weeks  # Positive = improving

            velocity[keyword] = {
                "current": current_pos,
                "velocity": round(vel, 2),
                "direction": "📈" if vel > 0 else "📉" if vel < 0 else "➡️",
                "prediction_4w": max(1, round(current_pos - vel * 4))  # Where we'll be in 4 weeks
            }

    warroom["velocity"] = velocity
    save_warroom(warroom)
    return velocity

def generate_counter_plan(keyword):
    """Genereer een counter-plan als we op een keyword zakken."""
    warroom = load_warroom()

    prompt = f"""We zakken op het keyword "{keyword}" in Google. Genereer een counter-attack plan.

Context:
- We zijn aibuildermarketplace.com (AI tools vergelijking/affiliate)
- Het keyword is relevant voor onze niche

Genereer JSON:
{{
    "keyword": "{keyword}",
    "immediate_actions": ["Actie 1", "Actie 2", "Actie 3"],
    "content_update": "Wat moet er aan het artikel veranderen",
    "link_building": "Specifieke backlink strategie",
    "timeline": "Verwachte recovery tijd",
    "priority": "CRITICAL|HIGH|MEDIUM"
}}"""

    try:
        response = ask_victor(prompt, [])
        json_match = response[response.find("{"):response.rfind("}")+1]
        plan = json.loads(json_match)
        plan["generated"] = datetime.now().isoformat()

        warroom["counter_plans"].append(plan)
        warroom["counter_plans"] = warroom["counter_plans"][-20:]
        save_warroom(warroom)
        return plan
    except Exception as e:
        log(f"Counter plan error: {e}")
        return None

# ── 16F: OMEGA PROTOCOL ORCHESTRATOR ──────────────────────────────────────

def omega_cycle():
    """Volledige Omega Protocol cyclus."""
    actions = []

    # Auto-Monetize
    try:
        opps = scan_missed_affiliate_opportunities()
        if opps:
            actions.append(f"💰 Monetize: {len(opps)} gemiste affiliate kansen gevonden")
        comm_opt = optimize_commissions()
        if comm_opt.get("recommendations"):
            actions.append(f"📊 Commission optimizer: {len(comm_opt['recommendations'])} aanbevelingen")
            for rec in comm_opt["recommendations"][:2]:
                add_digest_item("monetize", rec, priority=8)
    except Exception as e:
        log(f"Monetize error: {e}")

    # Content Fortress
    try:
        eeat = score_eeat()
        if eeat:
            low_scores = [s for s, d in eeat.items() if d.get("overall", 0) < 40]
            if low_scores:
                actions.append(f"🏰 E-E-A-T: {len(low_scores)} artikelen onder score 40")
            avg_score = sum(d.get("overall", 0) for d in eeat.values()) / max(len(eeat), 1)
            actions.append(f"🏰 Gemiddelde E-E-A-T score: {avg_score:.0f}/100")
        facts = fact_check_articles()
        if facts:
            actions.append(f"📋 Fact-check: {len(facts)} verouderde claims gevonden")
    except Exception as e:
        log(f"Fortress error: {e}")

    # War Room
    try:
        battles, victories = detect_ranking_battles()
        if battles:
            actions.append(f"⚔️ War Room: {len(battles)} ranking battles gedetecteerd!")
            for battle in battles[:2]:
                if battle.get("severity") == "CRITICAL":
                    bot.send_message(ADMIN_ID, f"🚨 RANKING ALERT: '{battle['keyword']}' dropped {battle['drop']} posities! (nu #{battle['current_position']})")
        if victories:
            actions.append(f"🏆 Victories: {len(victories)} keywords in top 3!")
            for v in victories[:2]:
                add_digest_item("victories", f"🏆 #{v['position']} voor '{v['keyword']}'", priority=7)
        velocity = calculate_ranking_velocity()
        if velocity:
            improving = sum(1 for v in velocity.values() if v.get("velocity", 0) > 0)
            declining = sum(1 for v in velocity.values() if v.get("velocity", 0) < 0)
            actions.append(f"📊 Velocity: {improving} stijgend, {declining} dalend")
    except Exception as e:
        log(f"War room error: {e}")

    # Self-Evolution
    try:
        perf = analyze_cycle_performance()
        if perf:
            actions.append(f"🧬 Self-analysis: {len(perf)} modules geanalyseerd")
        tunings = auto_tune_parameters()
        if tunings:
            actions.append(f"🔧 Auto-tune: {len(tunings)} optimalisaties voorgesteld")
    except Exception as e:
        log(f"Evolution error: {e}")

    # Viral (weekly only)
    try:
        if datetime.now().weekday() == 2:  # Wednesday
            magnets = generate_link_magnet_ideas()
            if magnets:
                actions.append(f"🧲 Viral: {len(magnets)} link magnet ideeën gegenereerd")
    except Exception as e:
        log(f"Viral error: {e}")

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


@bot.message_handler(commands=['audit'])
def cmd_audit(message):
    """Technische SEO audit."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔍 Volledige technische SEO audit starten...")
    bot.send_chat_action(message.chat.id, 'typing')

    result = full_site_audit()
    score = result["score"]
    emoji = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"

    msg = f"🔍 Technical SEO Audit\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{emoji} Health Score: {score}/100\n"
    msg += f"📄 Pagina's gescand: {result['total_pages']}\n\n"
    msg += f"🚨 Kritiek: {result['critical']}\n"
    msg += f"⚠️ Hoog: {result['high']}\n"
    msg += f"📋 Medium: {result['medium']}\n"
    msg += f"ℹ️ Laag: {result['low']}\n"
    msg += f"\n✅ Auto-gefixed: {len(result.get('fixes', []))}\n"

    if result.get("fixes"):
        msg += "\n🔧 Fixes:\n"
        for fix in result["fixes"][:8]:
            msg += f"  ✓ {fix}\n"

    # Top issues (niet gefixed)
    unfixed = [i for i in result.get("issues", []) if not i.get("auto_fixable")]
    if unfixed:
        msg += "\n⚠️ Handmatig nodig:\n"
        for i in unfixed[:5]:
            msg += f"  - {i['issue'][:60]}\n"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['trends'])
def cmd_trends(message):
    """Trend Radar — trending AI topics."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "status"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "scan":
        bot.reply_to(message, "📡 Trend Radar scannen...")
        trend_data = scan_trending_topics()
        hot = trend_data.get("hot_topics", [])
        opps = trend_data.get("opportunities", [])

        msg = f"📡 Trend Radar — Scan Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        if hot:
            msg += "🔥 Hot Topics:\n"
            for t in hot[:5]:
                urgency_emoji = "🔴" if t.get("urgency") == "high" else "🟡" if t.get("urgency") == "medium" else "🟢"
                msg += f"  {urgency_emoji} {t.get('topic', '?')}\n"
                if t.get("article_idea"):
                    msg += f"    → Artikel: {t['article_idea'][:50]}\n"
        else:
            msg += "Geen nieuwe hot topics gevonden.\n"

        if opps:
            msg += "\n💡 Kansen:\n"
            for o in opps[:3]:
                msg += f"  - {o}\n"

        bot.reply_to(message, msg)

    elif action == "write":
        bot.reply_to(message, "🔥 Trending artikel schrijven...")
        slug = auto_write_trend_article()
        if slug:
            bot.reply_to(message, f"✅ Trending artikel geschreven en live: {slug}")
        else:
            bot.reply_to(message, "❌ Geen urgent trending topics om over te schrijven.")

    else:
        trends = load_trends()
        msg = f"📡 Trend Radar Status\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"📊 Gedetecteerde trends: {len(trends.get('detected', []))}\n"
        msg += f"📝 Artikelen geschreven: {len(trends.get('articles_written', []))}\n"
        msg += f"🕐 Laatste scan: {trends.get('last_scan', 'nooit')}\n"

        recent = [t for t in trends.get("detected", [])[-10:]
                  if t.get("source") == "ai_analysis"]
        if recent:
            msg += "\n🔥 Recente topics:\n"
            for t in recent[:5]:
                msg += f"  - {t.get('keyword', '?')}: {t.get('article_idea', '')[:40]}\n"

        msg += "\nGebruik /trends scan of /trends write"
        bot.reply_to(message, msg)


@bot.message_handler(commands=['translate'])
def cmd_translate(message):
    """Vertaal artikelen naar Engels."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)

    bot.send_chat_action(message.chat.id, 'typing')

    if len(parts) > 1 and parts[1] == "run":
        bot.reply_to(message, "🌍 Artikelen vertalen naar Engels...")
        translated = translation_batch(max_articles=3)
        if translated:
            msg = f"🌍 {len(translated)} artikelen vertaald!\n\n"
            msg += "\n".join(f"  ✅ {s}" for s in translated)
        else:
            msg = "🌍 Geen nieuwe artikelen om te vertalen."
        bot.reply_to(message, msg)
    else:
        trans = load_translations()
        en_path = f"{REPO_ROOT}/en"
        en_count = len(os.listdir(en_path)) if os.path.isdir(en_path) else 0
        b2b_path = f"{REPO_ROOT}/b2b"
        nl_count = len([f for f in os.listdir(b2b_path) if f.endswith('.html')]) if os.path.isdir(b2b_path) else 0

        msg = f"🌍 Multi-Language Status\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🇳🇱 Nederlands: {nl_count} artikelen\n"
        msg += f"🇬🇧 Engels: {en_count} artikelen\n"
        msg += f"📊 Vertaald: {en_count}/{nl_count} ({en_count/nl_count*100:.0f}%)\n" if nl_count > 0 else ""
        msg += f"\nGebruik /translate run om te starten."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['heal'])
def cmd_heal(message):
    """Self-healing status en handmatige check."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔧 Self-healing check uitvoeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    incidents, fixes = self_healing_check()
    healing = load_healing()

    msg = f"🔧 Self-Healing System\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if not incidents and not fixes:
        msg += "✅ Alles gezond! Geen problemen gedetecteerd.\n"
    else:
        if fixes:
            msg += f"🔧 Auto-fixes ({len(fixes)}):\n"
            for f in fixes:
                msg += f"  ✓ {f}\n"

        if incidents:
            msg += f"\n⚠️ Incidenten ({len(incidents)}):\n"
            for i in incidents:
                sev = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(i["severity"], "⚪")
                msg += f"  {sev} {i['detail']}\n"

    # Uptime stats
    checks = healing.get("uptime_checks", [])
    if checks:
        avg_time = sum(c.get("response_time", 0) for c in checks) / len(checks)
        msg += f"\n📈 Uptime: {len(checks)} checks, gem. {avg_time:.2f}s"

    # Totaal stats
    stats = healing.get("stats", {})
    msg += f"\n📊 Totaal: {stats.get('total_fixes', 0)} fixes, {stats.get('total_incidents', 0)} incidenten"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['neural'])
def cmd_neural(message):
    """Volledige Neural Command Center cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🧠 Neural Command Center activeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = neural_command_cycle()
    if actions:
        msg = "🧠 Neural Command Center — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "🧠 Neural Command Center: alles stabiel."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['panel'])
def cmd_panel(message):
    """Interactief dashboard panel met inline buttons."""
    if message.from_user.id != ADMIN_ID:
        return
    keyboard = build_main_dashboard_keyboard()
    bot.send_message(
        message.chat.id,
        "🧠 Victor 17.0 Omega — Command Center\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nKies een module:",
        reply_markup=keyboard
    )


@bot.message_handler(commands=['conversions'])
def cmd_conversions(message):
    """Conversion intelligence analyse."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "📊 Conversion analyse draaien...")
    bot.send_chat_action(message.chat.id, 'typing')

    conv = analyze_article_conversions()
    top = conv.get("top_performers", [])
    patterns = conv.get("winning_patterns", [])

    msg = "📊 Conversion Intelligence\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📈 Totaal geanalyseerd: {len(conv.get('articles', {}))} artikelen\n\n"

    if top:
        msg += "🏆 Top Performers:\n"
        for i, t in enumerate(top[:5], 1):
            msg += f"  {i}. {t['slug'][:30]}: {t['score']:.0f}pts | {t['clicks']}↗ | €{t['revenue']:.0f}\n"

    if patterns:
        msg += "\n🧬 Winnende Patronen:\n"
        for p in patterns[:5]:
            msg += f"  - {p['insight']}\n"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['dna'])
def cmd_dna(message):
    """Content DNA analyse."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "analyze"

    bot.send_chat_action(message.chat.id, 'typing')

    if action.startswith("apply "):
        slug = action.replace("apply ", "").strip()
        bot.reply_to(message, f"🧬 DNA toepassen op {slug}...")
        result = apply_dna_to_article(slug)
        if result:
            bot.reply_to(message, f"✅ {slug} geoptimaliseerd met winning DNA!")
        else:
            bot.reply_to(message, f"❌ Kon DNA niet toepassen op {slug}")
    else:
        bot.reply_to(message, "🧬 Content DNA analyseren...")
        dna = analyze_content_dna()

        if not dna:
            bot.reply_to(message, "❌ Te weinig artikelen voor DNA analyse (min 5)")
            return

        blueprint = dna.get("blueprint", {})
        qual = blueprint.get("qualitative", {})
        scores = dna.get("article_scores", {})

        msg = "🧬 Content DNA Blueprint\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "📐 Ideale Metrics:\n"
        for metric in ["word_count", "h2_count", "cta_count", "aff_links", "table_count", "list_items"]:
            if metric in blueprint:
                msg += f"  {metric}: {blueprint[metric]['ideal']:.0f} (gem: {blueprint[metric]['average']:.0f})\n"

        if qual:
            msg += f"\n📝 Stijl:\n"
            if qual.get("tone"):
                msg += f"  Toon: {qual['tone'][:60]}\n"
            if qual.get("cta_style"):
                msg += f"  CTA: {qual['cta_style'][:60]}\n"

        if scores:
            avg = sum(scores.values()) / len(scores)
            msg += f"\n📊 DNA Match: gem. {avg:.0f}%"
            worst = sorted(scores.items(), key=lambda x: x[1])[:3]
            msg += "\n\n⚠️ Laagste match:\n"
            for slug, score in worst:
                msg += f"  {slug[:30]}: {score:.0f}%\n"
            msg += f"\nGebruik /dna apply <slug> om te verbeteren"

        bot.reply_to(message, msg)


@bot.message_handler(commands=['backlinks'])
def cmd_backlinks(message):
    """Backlink Hunter."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "status"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "hunt":
        bot.reply_to(message, "🔗 Backlink kansen jagen...")
        found, emails = backlink_batch()
        msg = f"🔗 Backlink Hunt Resultaat\n\n"
        msg += f"🔍 Nieuwe kansen: {found}\n"
        msg += f"📧 Outreach emails: {emails}\n"
        bot.reply_to(message, msg)
    elif action == "outreach":
        bl = load_backlinks()
        ready = [o for o in bl.get("opportunities", []) if o.get("outreach_email")]
        if ready:
            msg = "📧 Klaar om te versturen:\n\n"
            for o in ready[-3:]:
                msg += f"🌐 {o['url'][:50]}\n"
                msg += f"📧 {o['outreach_email'][:200]}\n\n"
        else:
            msg = "Nog geen outreach emails klaar. Gebruik /backlinks hunt"
        bot.reply_to(message, msg)
    else:
        bl = load_backlinks()
        msg = f"🔗 Backlink Hunter Status\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🔍 Kansen gevonden: {len(bl.get('opportunities', []))}\n"
        msg += f"📧 Outreach verstuurd: {len(bl.get('outreach_sent', []))}\n"
        msg += f"🕐 Laatste hunt: {bl.get('stats', {}).get('last_hunt', 'nooit')}\n"
        msg += f"\nGebruik /backlinks hunt of /backlinks outreach"
        bot.reply_to(message, msg)


@bot.message_handler(commands=['ab2'])
def cmd_ab2(message):
    """A/B Testing Engine 2.0."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    action = parts[1] if len(parts) > 1 else "status"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "create" and len(parts) > 2:
        slug = parts[2]
        bot.reply_to(message, f"🧪 A/B test starten voor {slug}...")
        test, error = create_ab2_test(slug, "cta_color")
        if test:
            msg = f"✅ A/B Test gestart!\n"
            msg += f"  Artikel: {slug}\n"
            msg += f"  Type: CTA kleuren\n"
            msg += f"  Varianten: {len(test['variants_data'])}\n"
            msg += f"  Duur: {test['days_per_variant'] * len(test['variants_data'])} dagen"
        else:
            msg = f"❌ {error}"
        bot.reply_to(message, msg)
    elif action == "check":
        actions = check_ab2_tests()
        if actions:
            msg = "🧪 A/B Test Updates:\n\n" + "\n".join(f"  {a}" for a in actions)
        else:
            msg = "🧪 Geen A/B test updates."
        bot.reply_to(message, msg)
    else:
        ab2 = load_ab2()
        active = [t for t in ab2["tests"] if t["status"] == "active"]
        completed = ab2.get("completed", [])

        msg = f"🧪 A/B Testing 2.0\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🔄 Actieve tests: {len(active)}\n"
        msg += f"✅ Afgerond: {len(completed)}\n"

        if active:
            msg += "\n📋 Actief:\n"
            for t in active:
                msg += f"  🧪 {t['slug']}: {t['type']} (variant {t['current_variant']+1}/{len(t['variants_data'])})\n"

        if completed:
            msg += "\n🏆 Laatste winnaars:\n"
            for c in completed[-3:]:
                msg += f"  ✓ {c['slug']}: {c['winner']} ({c['clicks']} clicks)\n"

        msg += f"\nGebruik /ab2 create <slug> of /ab2 check"
        bot.reply_to(message, msg)


@bot.message_handler(commands=['scorecard'])
def cmd_scorecard(message):
    """Visueel scorecard rapport."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    scorecard = generate_scorecard()
    bot.reply_to(message, scorecard)


@bot.message_handler(commands=['leaderboard'])
def cmd_leaderboard(message):
    """Artikel leaderboard."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    lb = generate_leaderboard()
    bot.reply_to(message, lb)


@bot.message_handler(commands=['hivemind'])
def cmd_hivemind(message):
    """Volledige Hive Mind cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🧠 Hive Mind activeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = hive_mind_cycle()
    if actions:
        msg = "🧠 Hive Mind — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "🧠 Hive Mind: alles up-to-date."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['validate'])
def cmd_validate(message):
    """Live site validatie."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔍 Live site valideren...")
    bot.send_chat_action(message.chat.id, 'typing')

    results = validate_full_site(max_pages=15)
    passed = sum(1 for r in results if r["ok"])
    failed = sum(1 for r in results if not r["ok"])

    msg = f"🔍 Live Site Validatie\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"✅ OK: {passed}\n❌ Problemen: {failed}\n📊 Totaal: {len(results)}\n\n"

    if failed:
        msg += "⚠️ Problemen:\n"
        for r in results:
            if not r["ok"]:
                slug = r["url"].split("/")[-1].replace(".html", "")
                issues = ", ".join(i["detail"][:30] for i in r["issues"][:2])
                msg += f"  ❌ {slug[:25]}: {issues}\n"

    # Avg load time
    load_times = [r["load_time"] for r in results if r["load_time"] > 0]
    if load_times:
        avg = sum(load_times) / len(load_times)
        msg += f"\n⚡ Gem. laadtijd: {avg:.2f}s"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['freshness'])
def cmd_freshness(message):
    """Content freshness scan."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "scan"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "update":
        bot.reply_to(message, "🔄 Verouderde content updaten...")
        outdated, updated = freshness_scan_batch(max_articles=15)
        if updated:
            msg = f"🔄 {len(updated)} artikelen bijgewerkt:\n\n" + "\n".join(f"  ✅ {u}" for u in updated)
        else:
            msg = "✅ Geen artikelen hoeven geüpdatet te worden."
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🔄 Freshness scan draaien...")
        outdated, updated = freshness_scan_batch(max_articles=20)
        fresh = load_freshness()

        msg = f"🔄 Content Freshness\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"📊 Gescand: {len(fresh.get('articles', {}))} artikelen\n"
        msg += f"⚠️ Verouderd: {len(outdated)}\n"
        msg += f"✅ Auto-updated: {len(updated)}\n"

        if outdated:
            msg += "\n📉 Meest verouderd:\n"
            for o in outdated[:5]:
                msg += f"  ⚠️ {o['slug'][:30]}: score {o['freshness_score']}/100 ({o['age_days']}d oud)\n"

        msg += f"\nGebruik /freshness update om te fixen."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['journey'])
def cmd_journey(message):
    """Buyer journey mapping."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    action = parts[1] if len(parts) > 1 else "map"

    bot.send_chat_action(message.chat.id, 'typing')

    if action == "fill":
        bot.reply_to(message, "🗺️ Journey gaten vullen...")
        filled = auto_fill_journey_gap(max_articles=2)
        if filled:
            msg = f"🗺️ {len(filled)} journey artikelen geschreven:\n\n" + "\n".join(f"  ✅ {f}" for f in filled)
        else:
            msg = "✅ Alle journey gaten zijn al gevuld!"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🗺️ Buyer journey analyseren...")
        journey = map_buyer_journey()
        coverage = journey.get("coverage", {})
        gaps = journey.get("gaps", [])

        msg = f"🗺️ Buyer Journey Map\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for brand, cov in coverage.items():
            if brand not in VAULT:
                continue
            status = "✅" if cov["complete"] else "⚠️"
            msg += f"{status} {brand}:\n"
            msg += f"   Awareness: {'✅' if cov['awareness'] else '❌'} ({cov['awareness']})"
            msg += f"  Consider: {'✅' if cov['consideration'] else '❌'} ({cov['consideration']})"
            msg += f"  Decision: {'✅' if cov['decision'] else '❌'} ({cov['decision']})\n"

        if gaps:
            msg += f"\n🚨 {len(gaps)} gaten:\n"
            for g in gaps[:5]:
                msg += f"  ❌ {g['brand']} → {g['missing_stage']}: {g['suggested_title'][:40]}\n"
            msg += f"\nGebruik /journey fill om gaten te vullen."

        bot.reply_to(message, msg)


@bot.message_handler(commands=['roigate'])
def cmd_roigate(message):
    """ROI Gate — evalueer artikel voordat je schrijft."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)

    if len(parts) < 2:
        roi = load_roigate()
        msg = f"🎯 ROI Gate\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"✅ Goedgekeurd: {len(roi.get('approved', []))}\n"
        msg += f"❌ Afgewezen: {len(roi.get('rejected', []))}\n"
        msg += f"📊 Threshold: {roi.get('threshold', 30)} punten\n"
        msg += f"\nGebruik /roigate <keyword> [brand]"
        bot.reply_to(message, msg)
        return

    keyword = parts[1]
    brand = parts[2] if len(parts) > 2 else None

    bot.send_chat_action(message.chat.id, 'typing')
    evaluation = evaluate_article_roi(keyword, brand)

    emoji = "✅" if evaluation["approved"] else "❌"
    msg = f"🎯 ROI Gate — {keyword}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{emoji} Score: {evaluation['score']}/{evaluation['threshold']} threshold\n"
    msg += f"{'✅ GOEDGEKEURD — schrijven!' if evaluation['approved'] else '❌ AFGEWEZEN — niet rendabel'}\n\n"

    msg += "📊 Factoren:\n"
    for f in evaluation["factors"]:
        msg += f"  - {f}\n"

    est = evaluation.get("estimates", {})
    if est:
        msg += f"\n💰 Schatting:\n"
        msg += f"  Clicks/maand: ~{est.get('monthly_clicks', '?')}\n"
        msg += f"  Revenue/maand: €{est.get('monthly_revenue', 0):.2f}\n"
        msg += f"  Revenue/jaar: €{est.get('yearly_revenue', 0):.2f}\n"
        msg += f"  Tijd tot ranking: ~{est.get('time_to_rank_months', '?')} maanden"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['digest'])
def cmd_digest(message):
    """Smart daily digest."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    digest = generate_smart_digest()
    if digest:
        bot.reply_to(message, digest)
    else:
        bot.reply_to(message, "📋 Geen digest items — alles rustig!")


@bot.message_handler(commands=['omniscience'])
def cmd_omniscience(message):
    """Volledige Omniscience cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "👁️ Omniscience cyclus activeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = omniscience_cycle()
    if actions:
        msg = "👁️ Omniscience — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "👁️ Omniscience: alles optimaal."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['calendar'])
def cmd_calendar(message):
    """Toon en genereer content calendar."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    if len(parts) > 1 and parts[1] == "generate":
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, "📅 Content calendar genereren...")
        calendar = generate_content_calendar()
        if calendar:
            items = calendar.get("items", [])
            msg = "📅 Content Calendar — Gegenereerd\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for i, item in enumerate(items[:10], 1):
                status_emoji = "✅" if item.get("status") == "done" else "⏳"
                msg += f"{i}. {status_emoji} [{item.get('type', '?')}] {item.get('title', '?')[:50]}\n"
                msg += f"   ROI: {item.get('roi_score', '?')} | Brand: {item.get('brand', '?')}\n"
            msg += f"\n📊 Totaal: {len(items)} items gepland"
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, "📅 Kon geen calendar items genereren.")
    else:
        try:
            cal = json.loads(open(CALENDAR_FILE).read()) if os.path.exists(CALENDAR_FILE) else {}
        except:
            cal = {}
        items = cal.get("items", [])
        if items:
            msg = "📅 Content Calendar\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            pending = [i for i in items if i.get("status") != "done"]
            done = [i for i in items if i.get("status") == "done"]
            for i, item in enumerate(pending[:8], 1):
                msg += f"{i}. ⏳ [{item.get('type', '?')}] {item.get('title', '?')[:50]}\n"
                msg += f"   ROI: {item.get('roi_score', '?')} | Brand: {item.get('brand', '?')}\n"
            msg += f"\n📊 Pending: {len(pending)} | Done: {len(done)} | Totaal: {len(items)}"
        else:
            msg = "📅 Calendar is leeg. Gebruik /calendar generate om te plannen."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['calexec'])
def cmd_calexec(message):
    """Voer het volgende calendar item uit."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, "📅 Volgend calendar item uitvoeren...")
    result = execute_calendar_item()
    if result:
        bot.reply_to(message, f"✅ {result}")
    else:
        bot.reply_to(message, "📅 Geen pending items in de calendar. Gebruik /calendar generate")


@bot.message_handler(commands=['outreach'])
def cmd_outreach(message):
    """Email outreach campagne."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    if len(parts) > 1 and parts[1] == "run":
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, "📧 Outreach campagne starten...")
        results = run_outreach_campaign(max_emails=3)
        if results:
            msg = "📧 Outreach — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for r in results:
                emoji = "✅" if r.get("success") else "❌"
                msg += f"{emoji} {r.get('to', '?')} — {r.get('campaign', '?')}\n"
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, "📧 Geen outreach campagnes beschikbaar.")
    else:
        try:
            out = json.loads(open(OUTREACH_FILE).read()) if os.path.exists(OUTREACH_FILE) else {}
        except:
            out = {}
        campaigns = out.get("campaigns", [])
        sent = out.get("sent", [])
        msg = f"📧 Outreach Status\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"📋 Campagnes: {len(campaigns)}\n"
        msg += f"📤 Verstuurd: {len(sent)}\n"
        if sent:
            last = sent[-1]
            msg += f"\n📧 Laatste: {last.get('to', '?')} ({last.get('date', '?')})"
        bot.reply_to(message, msg)


@bot.message_handler(commands=['palace'])
def cmd_palace(message):
    """Victor Memory Palace — strategisch geheugen."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    if len(parts) > 1 and parts[1] == "update":
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, "🏛️ Memory Palace updaten...")
        update_memory_palace()
        bot.reply_to(message, "✅ Memory Palace bijgewerkt!")

    try:
        palace = json.loads(open(PALACE_FILE).read()) if os.path.exists(PALACE_FILE) else {}
    except:
        palace = {}

    msg = "🏛️ Victor Memory Palace\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Seasonal patterns
    seasons = palace.get("seasonal_patterns", {})
    if seasons:
        msg += "📅 Seizoenspatronen:\n"
        for month, data in list(seasons.items())[:3]:
            msg += f"  {month}: {data.get('top_topic', '?')} (clicks: {data.get('avg_clicks', '?')})\n"
        msg += "\n"

    # Brand trends
    trends = palace.get("brand_trends", {})
    if trends:
        msg += "📈 Brand Trends:\n"
        for brand, data in list(trends.items())[:4]:
            direction = "📈" if data.get("trend") == "up" else "📉" if data.get("trend") == "down" else "➡️"
            msg += f"  {direction} {brand}: {data.get('note', '?')}\n"
        msg += "\n"

    # Strategic insights
    insights = palace.get("quarterly_insights", [])
    if insights:
        msg += "🧠 Laatste Inzichten:\n"
        for ins in insights[-3:]:
            msg += f"  💡 {ins[:80]}\n"

    if not seasons and not trends and not insights:
        msg += "Leeg. Gebruik /palace update om te vullen."

    bot.reply_to(message, msg)


@bot.message_handler(commands=['dashboardv2'])
def cmd_dashboardv2(message):
    """Dashboard V2 met Chart.js."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, "📊 Dashboard V2 genereren...")

    html_path = generate_dashboard_v2()
    if html_path and os.path.exists(html_path):
        with open(html_path, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="📊 Victor Dashboard V2 — Open in browser")
    else:
        bot.reply_to(message, "❌ Dashboard V2 kon niet worden gegenereerd.")


@bot.message_handler(commands=['skynet'])
def cmd_skynet(message):
    """Volledige Skynet Protocol cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🛰️ Skynet Protocol activeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = skynet_cycle()
    if actions:
        msg = "🛰️ Skynet Protocol — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "🛰️ Skynet: alles draait optimaal."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['api'])
def cmd_api(message):
    """API server status."""
    if message.from_user.id != ADMIN_ID:
        return
    msg = f"🌐 Victor API Server\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📡 Port: {API_PORT}\n"
    msg += f"🔗 Endpoints:\n"
    msg += f"  GET /api/health — Healthcheck\n"
    msg += f"  GET /api/stats — Statistieken\n"
    msg += f"  GET /api/serp — SERP data\n"
    msg += f"  GET /api/calendar — Content calendar\n"
    msg += f"  GET /api/palace — Memory Palace\n"
    msg += f"  POST /api/webhook/github — GitHub webhook\n"
    msg += f"  POST /api/webhook/uptime — Uptime alerts\n"
    msg += f"  POST /api/trigger — Remote trigger\n\n"

    # Check if API log exists
    if os.path.exists(API_LOG_FILE):
        try:
            with open(API_LOG_FILE) as f:
                lines = f.readlines()[-5:]
            msg += "📋 Laatste requests:\n"
            for line in lines:
                msg += f"  {line.strip()}\n"
        except:
            pass
    else:
        msg += "📋 Nog geen requests ontvangen."

    bot.reply_to(message, msg)


@bot.message_handler(commands=['revenue2'])
def cmd_revenue2(message):
    """Revenue Radar — geavanceerde revenue tracking."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    tracked = track_revenue_per_article()
    forecast = revenue_forecast()

    msg = "💰 Revenue Radar\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📊 Geschatte maandelijkse revenue: €{forecast.get('total_monthly', 0):.2f}\n"
    msg += f"📈 Geschatte jaarlijkse revenue: €{forecast.get('total_yearly', 0):.2f}\n\n"

    # Top articles
    top = forecast.get("top_articles", [])[:5]
    if top:
        msg += "🏆 Top Earners:\n"
        for i, (slug, rev) in enumerate(top, 1):
            msg += f"  {i}. {slug[:35]} — €{rev:.2f}/mo\n"

    # Brand breakdown
    brands = forecast.get("brand_breakdown", {})
    if brands:
        msg += "\n💼 Per Brand:\n"
        for brand, rev in sorted(brands.items(), key=lambda x: x[1], reverse=True):
            msg += f"  {brand}: €{rev:.2f}/mo\n"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['alerts'])
def cmd_alerts(message):
    """Money alerts — significante traffic veranderingen."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    alerts = revenue_money_alerts()
    radar = load_revenue_radar()
    all_alerts = radar.get("alerts", [])[-10:]

    if all_alerts:
        msg = "🚨 Money Alerts\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for a in all_alerts:
            emoji = "📈" if a.get("type") == "spike" else "📉"
            msg += f"{emoji} {a.get('slug', '?')[:30]}\n"
            msg += f"   {a.get('change', '?')} | Impact: {a.get('revenue_impact', '?')}\n\n"
    else:
        msg = "🚨 Geen recente money alerts. Alles stabiel!"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['social2'])
def cmd_social2(message):
    """Social Swarm — genereer multi-platform content."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    slug = parts[1] if len(parts) > 1 else None

    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, "📱 Social posts genereren...")

    posts = generate_social_posts(slug)
    if posts:
        msg = f"📱 Social Swarm — {posts.get('slug', '?')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "🐦 Twitter Thread:\n"
        for i, tweet in enumerate(posts.get("twitter_thread", []), 1):
            msg += f"  {i}. {tweet[:100]}\n"
        msg += f"\n💼 LinkedIn:\n  {posts.get('linkedin_post', '')[:200]}...\n"
        msg += f"\n🔴 Reddit: {posts.get('reddit_title', '')[:80]}\n"
        msg += f"\n#️⃣ {' '.join(posts.get('hashtags', []))}"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "📱 Kon geen social posts genereren. Check of er artikelen zijn.")


@bot.message_handler(commands=['repurpose'])
def cmd_repurpose(message):
    """Content repurposing — 1 artikel → 5 formats."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /repurpose <slug>")
        return

    slug = parts[1]
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, f"🔄 {slug} repurposen naar 5 formats...")

    result = repurpose_content(slug)
    if result:
        msg = f"🔄 Repurposed: {slug}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🐦 Hook: {result.get('twitter_hook', '?')[:100]}\n\n"
        msg += "📱 Carousel slides:\n"
        for s in result.get("linkedin_carousel_slides", [])[:5]:
            msg += f"  • {s[:60]}\n"
        msg += f"\n📧 Newsletter: {result.get('newsletter_snippet', '?')[:120]}\n"
        msg += f"\n🎬 Video hook: {result.get('video_script_hook', '?')[:100]}"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "❌ Kon content niet repurposen.")


@bot.message_handler(commands=['predict2'])
def cmd_predict2(message):
    """Predictive Engine — seizoenspatronen + write-now alerts."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    seasonal = analyze_seasonal_patterns()
    write_alerts = generate_write_now_alerts()
    timing = generate_content_timing_plan()

    msg = "🔮 Predictive Engine\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if write_alerts:
        msg += "⚡ WRITE NOW Alerts:\n"
        for a in write_alerts[:5]:
            emoji = "🔴" if a.get("urgency") == "HIGH" else "🟡"
            msg += f"  {emoji} {a.get('topic', '?')[:40]}"
            if a.get("brand"):
                msg += f" [{a['brand']}]"
            msg += "\n"
        msg += "\n"

    if timing:
        msg += "🗓️ Content Timing Plan:\n"
        for t in timing[:3]:
            msg += f"  📅 {t.get('month', '?')}: {t.get('topics_count', 0)} topics (write by {t.get('write_before', '?')})\n"
        msg += "\n"

    current_month = datetime.now().strftime("%B")
    month_peaks = seasonal.get(current_month, [])
    if month_peaks:
        msg += f"📈 Deze maand ({current_month}) peaks: {len(month_peaks)} keywords"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['authority'])
def cmd_authority(message):
    """Authority Builder — topic clusters + PageRank."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    clusters = build_topic_clusters()
    cluster_auth = calculate_cluster_authority()

    msg = "🏛️ Authority Builder\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if cluster_auth:
        msg += "📊 Cluster Scores:\n"
        sorted_clusters = sorted(cluster_auth.items(), key=lambda x: x[1].get("authority_score", 0), reverse=True)
        for name, data in sorted_clusters[:8]:
            score = data.get("authority_score", 0)
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            msg += f"  {bar} {name} ({score})\n"
            msg += f"    📄 {data.get('articles', 0)} articles | 👁️ {data.get('total_clicks', 0)} clicks\n"
            if data.get("gaps"):
                msg += f"    ❌ Gaps: {', '.join(data['gaps'][:3])}\n"

    # Link opportunities
    link_opps = find_link_opportunities()
    if link_opps:
        msg += f"\n🔗 Top Link Opportunities ({len(link_opps)}):\n"
        for opp in link_opps[:3]:
            msg += f"  {opp['from'][:20]} → {opp['to'][:20]} ({opp['impact']})\n"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['portal'])
def cmd_portal(message):
    """Victor Live Portal genereren."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, "🌐 Live Portal genereren...")

    portal_path = generate_live_portal()
    if portal_path and os.path.exists(portal_path):
        with open(portal_path, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="🌐 Victor Live Portal — Open in browser\n\nOf host via: python3 -m http.server 8080 --directory /root/felix_hq/portal")
    else:
        bot.reply_to(message, "❌ Portal kon niet worden gegenereerd.")


@bot.message_handler(commands=['quantum'])
def cmd_quantum(message):
    """Volledige Quantum Core cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔮 Quantum Core activeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = quantum_cycle()
    if actions:
        msg = "🔮 Quantum Core — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "🔮 Quantum Core: alles optimaal."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['monetize'])
def cmd_monetize(message):
    """Auto-Monetize — scan gemiste affiliate kansen."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    bot.send_chat_action(message.chat.id, 'typing')

    if len(parts) > 1 and parts[1] == "inject":
        slug = parts[2] if len(parts) > 2 else None
        bot.reply_to(message, "💉 Affiliate links injecteren (dry run)...")
        injections = inject_affiliate_links(slug, dry_run=True)
        if injections:
            msg = "💉 Injection Preview (dry run)\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for inj in injections[:8]:
                msg += f"  📝 {inj['slug'][:30]} → {inj['brand']}\n"
            msg += f"\nGebruik /monetize inject! [slug] om echt te injecteren"
        else:
            msg = "Geen injection targets gevonden."
        bot.reply_to(message, msg)
    elif len(parts) > 1 and parts[1] == "inject!":
        slug = parts[2] if len(parts) > 2 else None
        bot.reply_to(message, "💉 Affiliate links LIVE injecteren...")
        injections = inject_affiliate_links(slug, dry_run=False)
        if injections:
            msg = f"✅ {len(injections)} affiliate links geïnjecteerd!"
        else:
            msg = "Geen links geïnjecteerd."
        bot.reply_to(message, msg)
    else:
        opps = scan_missed_affiliate_opportunities()
        comm = optimize_commissions()

        msg = "💰 Auto-Monetize Engine\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        if opps:
            msg += f"🔍 Gemiste kansen ({len(opps)}):\n"
            for o in opps[:6]:
                msg += f"  • {o['slug'][:25]} → {o['brand']} ({o['mentions']}x vermeld)\n"
            msg += "\n"

        recs = comm.get("recommendations", [])
        if recs:
            msg += "📊 Commission Optimizer:\n"
            for r in recs[:4]:
                msg += f"  {r}\n"
        else:
            msg += "📊 Alle brands presteren goed."

        msg += "\n\n💡 /monetize inject — preview link injection"
        bot.reply_to(message, msg)


@bot.message_handler(commands=['eeat'])
def cmd_eeat(message):
    """E-E-A-T Content Fortress scoring."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    slug = parts[1] if len(parts) > 1 else None
    bot.send_chat_action(message.chat.id, 'typing')

    eeat = score_eeat(slug)
    if not eeat:
        bot.reply_to(message, "❌ Geen artikelen gevonden om te scoren.")
        return

    msg = "🏰 Content Fortress — E-E-A-T Scores\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    sorted_scores = sorted(eeat.items(), key=lambda x: x[1].get("overall", 0))

    if slug and slug in eeat:
        # Single article detail
        s = eeat[slug]
        msg += f"📄 {slug}\n"
        msg += f"  Grade: {s['grade']} ({s['overall']}/100)\n"
        msg += f"  🧪 Experience: {s['experience']}/100\n"
        msg += f"  🎓 Expertise: {s['expertise']}/100\n"
        msg += f"  👑 Authority: {s['authority']}/100\n"
        msg += f"  🔒 Trust: {s['trust']}/100\n\n"

        signals = generate_trust_signals(slug)
        if signals:
            msg += "💡 Verbeteringen:\n"
            for sig in signals:
                msg += f"  [{sig['impact']}] {sig['action']}\n"
    else:
        # Overview: worst 5 + best 5
        msg += "❌ Laagste scores:\n"
        for s_slug, s_data in sorted_scores[:5]:
            msg += f"  {s_data['grade']} {s_slug[:30]} ({s_data['overall']:.0f})\n"
        msg += "\n✅ Hoogste scores:\n"
        for s_slug, s_data in sorted_scores[-5:]:
            msg += f"  {s_data['grade']} {s_slug[:30]} ({s_data['overall']:.0f})\n"

        avg = sum(d.get("overall", 0) for d in eeat.values()) / max(len(eeat), 1)
        msg += f"\n📊 Gemiddeld: {avg:.0f}/100 | Totaal: {len(eeat)} artikelen"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['viral'])
def cmd_viral(message):
    """Viral Loop Generator — link magnets + stat cards."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    bot.send_chat_action(message.chat.id, 'typing')

    if len(parts) > 1 and parts[1] == "table":
        bot.reply_to(message, "📊 Vergelijkingstabel genereren...")
        table = generate_comparison_table()
        if table:
            # Save as HTML file and send
            table_path = "/root/felix_hq/viral_table.html"
            with open(table_path, 'w') as f:
                f.write(table)
            with open(table_path, 'rb') as f:
                bot.send_document(message.chat.id, f, caption="📊 Embeddable vergelijkingstabel")
        else:
            bot.reply_to(message, "❌ Kon geen tabel genereren.")
    elif len(parts) > 1 and parts[1] == "cards":
        slug = parts[2] if len(parts) > 2 else None
        if not slug:
            bot.reply_to(message, "Gebruik: /viral cards <slug>")
            return
        cards = generate_stat_cards(slug)
        if cards:
            msg = f"📇 Stat Cards — {slug}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for i, card in enumerate(cards, 1):
                msg += f"{i}. 💬 \"{card.get('text', '?')}\"\n   Type: {card.get('type', '?')}\n\n"
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, "❌ Kon geen stat cards genereren.")
    else:
        magnets = generate_link_magnet_ideas()
        if magnets:
            msg = "🧲 Link Magnet Ideeën\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for i, m in enumerate(magnets, 1):
                msg += f"{i}. 🧲 {m.get('name', '?')}\n"
                msg += f"   {m.get('description', '?')[:60]}\n"
                msg += f"   SEO: {m.get('seo_value', '?')[:40]} | Backlinks: {m.get('backlink_potential', '?')}\n\n"
        else:
            msg = "🧲 Geen link magnet ideeën beschikbaar."
        bot.reply_to(message, msg)


@bot.message_handler(commands=['evolve'])
def cmd_evolve(message):
    """Self-Evolution — performance analyse + verbetervoorstellen."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    perf = analyze_cycle_performance()
    tunings = auto_tune_parameters()
    proposals = generate_improvement_proposals()

    msg = "🧬 Self-Evolution Core\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    msg += "📊 Module Performance:\n"
    for module, data in perf.items():
        eff = data.get("efficiency", 0)
        err = data.get("error_rate", 0)
        status = "✅" if err < 20 else "⚠️" if err < 50 else "❌"
        msg += f"  {status} {module}: {data['runs']} runs, {eff:.1f} actions/run, {err:.0f}% errors\n"

    if tunings:
        msg += "\n🔧 Auto-Tune Suggesties:\n"
        for t in tunings[:3]:
            msg += f"  ⚡ {t['module']}: {t['issue']}\n"

    if proposals:
        msg += "\n💡 Verbetervoorstellen:\n"
        for p in proposals[:3]:
            msg += f"  [{p.get('priority', '?')}] {p.get('title', '?')}\n"
            msg += f"    → {p.get('solution', '?')[:60]}\n"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['warroom'])
def cmd_warroom(message):
    """War Room — ranking battles + velocity + counter-plans."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_chat_action(message.chat.id, 'typing')

    battles, victories = detect_ranking_battles()
    velocity = calculate_ranking_velocity()

    msg = "⚔️ War Room\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if victories:
        msg += "🏆 Victories (Top 3 posities):\n"
        for v in victories[:5]:
            msg += f"  🥇 #{v['position']} — {v['keyword'][:40]}\n"
        msg += "\n"

    if battles:
        msg += "⚔️ Active Battles:\n"
        for b in battles[:5]:
            emoji = "🚨" if b.get("severity") == "CRITICAL" else "⚠️"
            msg += f"  {emoji} {b['keyword'][:30]} — dropped {b['drop']} (#{b['prev_position']}→#{b['current_position']})\n"
        msg += "\n"

    if velocity:
        improving = [(k, v) for k, v in velocity.items() if v.get("velocity", 0) > 0.5]
        declining = [(k, v) for k, v in velocity.items() if v.get("velocity", 0) < -0.5]

        if improving:
            msg += f"📈 Stijgende keywords ({len(improving)}):\n"
            for kw, v in sorted(improving, key=lambda x: x[1]["velocity"], reverse=True)[:3]:
                msg += f"  📈 {kw[:30]} (+{v['velocity']:.1f}/week) → predicted #{v['prediction_4w']}\n"

        if declining:
            msg += f"\n📉 Dalende keywords ({len(declining)}):\n"
            for kw, v in sorted(declining, key=lambda x: x[1]["velocity"])[:3]:
                msg += f"  📉 {kw[:30]} ({v['velocity']:.1f}/week) → predicted #{v['prediction_4w']}\n"

    if not battles and not victories and not velocity:
        msg += "Nog geen SERP data. Gebruik /serp update eerst."

    bot.reply_to(message, msg)


@bot.message_handler(commands=['counter'])
def cmd_counter(message):
    """Genereer counter-attack plan voor een keyword."""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Gebruik: /counter <keyword>")
        return

    keyword = parts[1]
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, f"⚔️ Counter-plan genereren voor '{keyword}'...")

    plan = generate_counter_plan(keyword)
    if plan:
        msg = f"⚔️ Counter-Attack Plan — {keyword}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"🎯 Priority: {plan.get('priority', '?')}\n"
        msg += f"⏱️ Timeline: {plan.get('timeline', '?')}\n\n"
        msg += "⚡ Directe acties:\n"
        for a in plan.get("immediate_actions", []):
            msg += f"  • {a}\n"
        msg += f"\n📝 Content: {plan.get('content_update', '?')}\n"
        msg += f"🔗 Links: {plan.get('link_building', '?')}"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "❌ Kon geen counter-plan genereren.")


@bot.message_handler(commands=['omega'])
def cmd_omega(message):
    """Volledige Omega Protocol cyclus."""
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🌀 Omega Protocol activeren...")
    bot.send_chat_action(message.chat.id, 'typing')

    actions = omega_cycle()
    if actions:
        msg = "🌀 Omega Protocol — Resultaten\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(f"  ✅ {a}" for a in actions)
    else:
        msg = "🌀 Omega: alles optimaal."
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
    bot.reply_to(message, """Victor 17.0 Omega — Commando's:

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

🧠 Neural Command Center:
/audit — Technische SEO audit + auto-fix
/trends [scan|write] — Trending AI topics
/translate [run] — Artikelen naar Engels
/heal — Self-healing check
/neural — Volledige neural cyclus
/panel — Interactief dashboard met buttons

🧠 Hive Mind:
/conversions — Conversion intelligence analyse
/dna [apply slug] — Content DNA blueprint
/backlinks [hunt|outreach] — Backlink kansen jagen
/ab2 [create slug|check] — A/B Testing 2.0
/scorecard — Visueel ASCII scorecard
/leaderboard — Artikel ranking leaderboard
/hivemind — Volledige Hive Mind cyclus

👁️ Omniscience:
/validate — Live site validatie
/freshness [update] — Content versheid check
/journey [fill] — Buyer journey mapping
/roigate <keyword> [brand] — ROI voorspelling
/digest — Smart daily digest
/omniscience — Volledige Omniscience cyclus

🛰️ Skynet Protocol:
/calendar [generate] — Content calendar beheren
/calexec — Volgend calendar item uitvoeren
/outreach [run] — Email outreach campagnes
/palace [update] — Memory Palace strategisch geheugen
/dashboardv2 — Chart.js dashboard V2
/api — API server status & endpoints
/skynet — Volledige Skynet cyclus

🔮 Quantum Core:
/revenue2 — Revenue Radar geavanceerde tracking
/alerts — Money alerts (traffic spikes/drops)
/social2 [slug] — Social Swarm multi-platform posts
/repurpose <slug> — 1 artikel → 5 content formats
/predict2 — Predictive Engine seizoenspatronen
/authority — Topic clusters + PageRank simulatie
/portal — Live web portal genereren
/quantum — Volledige Quantum Core cyclus

🌀 Omega Protocol:
/monetize [inject|inject!] — Auto-monetize gemiste affiliate kansen
/eeat [slug] — E-E-A-T scoring + trust signals
/viral [table|cards slug] — Viral loops + link magnets
/evolve — Self-evolution + verbetervoorstellen
/warroom — Ranking battles + velocity tracker
/counter <keyword> — Counter-attack plan genereren
/omega — Volledige Omega Protocol cyclus

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


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle inline keyboard button presses."""
    if call.from_user.id != ADMIN_ID:
        return

    data = call.data
    chat_id = call.message.chat.id

    try:
        bot.answer_callback_query(call.id, "⏳ Even laden...")

        if data == "dash_status":
            report = generate_status_report()
            bot.send_message(chat_id, report)

        elif data == "dash_serp":
            report = generate_serp_report()
            bot.send_message(chat_id, report)

        elif data == "dash_revenue":
            estimates = calculate_article_revenue()
            report = generate_revenue_report()
            bot.send_message(chat_id, report)

        elif data == "dash_competitors":
            comps = load_competitors()
            msg = f"🕵️ Competitors: {len(comps.get('scans', []))} scans, "
            msg += f"{len(comps.get('skyscraper_targets', []))} targets"
            bot.send_message(chat_id, msg)

        elif data == "dash_autopilot":
            ap = load_autopilot()
            msg = f"🤖 Autopilot: {len(ap.get('chain_reactions', []))} chains, "
            msg += f"{len(ap.get('recycled_articles', []))} recycled"
            bot.send_message(chat_id, msg)

        elif data == "dash_domination":
            prog = load_programmatic()
            sd = load_schema_data()
            lg = load_linkgraph()
            msg = f"🔥 Domination Matrix:\n"
            msg += f"  🏭 Programmatic: {len(prog.get('generated_pages', []))} pages\n"
            msg += f"  🏷️ Schema: {len(sd.get('articles_with_schema', []))} articles\n"
            msg += f"  🔗 Link graph: {len(lg.get('pages', {}))} pages gescand"
            bot.send_message(chat_id, msg)

        elif data == "dash_schema":
            sd = load_schema_data()
            msg = f"🏷️ Schema: {len(sd.get('articles_with_schema', []))} artikelen met markup"
            bot.send_message(chat_id, msg)

        elif data == "dash_links":
            lg = load_linkgraph()
            recs = lg.get("recommendations", [])
            msg = f"🔗 Link Graph: {len(lg.get('pages', {}))} pages, {len(recs)} aanbevelingen"
            bot.send_message(chat_id, msg)

        elif data == "dash_brain":
            skills = load_skills()
            msg = f"🧠 Brain: {len(skills.get('solutions', {}))} oplossingen geleerd"
            bot.send_message(chat_id, msg)

        elif data == "dash_briefing":
            briefing = generate_daily_briefing()
            bot.send_message(chat_id, briefing)

        elif data == "dash_audit":
            audit = load_audit()
            audits = audit.get("audits", [])
            if audits:
                last = audits[-1]
                msg = f"🔍 Laatste audit: score {last.get('score', '?')}/100, {last.get('auto_fixed', 0)} fixes"
            else:
                msg = "🔍 Nog geen audit gedaan. Gebruik /audit"
            bot.send_message(chat_id, msg)

        elif data == "dash_translate":
            trans = load_translations()
            msg = f"🌍 Vertaald: {len(trans.get('translated', []))} artikelen naar Engels"
            bot.send_message(chat_id, msg)

        elif data == "dash_scorecard":
            scorecard = generate_scorecard()
            bot.send_message(chat_id, scorecard)

        elif data == "dash_leaderboard":
            lb = generate_leaderboard()
            bot.send_message(chat_id, lb)

        elif data == "dash_dna":
            dna = load_dna()
            scores = dna.get("article_scores", {})
            avg = sum(scores.values()) / max(len(scores), 1) if scores else 0
            msg = f"🧬 DNA Match: gem. {avg:.0f}% | {len(scores)} artikelen geanalyseerd"
            bot.send_message(chat_id, msg)

        elif data == "dash_backlinks":
            bl = load_backlinks()
            msg = f"🔗 Backlinks: {len(bl.get('opportunities', []))} kansen, {len(bl.get('outreach_sent', []))} outreach"
            bot.send_message(chat_id, msg)

        elif data == "dash_calendar":
            try:
                cal = json.loads(open(CALENDAR_FILE).read()) if os.path.exists(CALENDAR_FILE) else {}
            except:
                cal = {}
            items = cal.get("items", [])
            pending = [i for i in items if i.get("status") != "done"]
            msg = f"📅 Calendar: {len(pending)} pending, {len(items)} totaal"
            if pending:
                next_item = pending[0]
                msg += f"\n▶️ Volgende: [{next_item.get('type', '?')}] {next_item.get('title', '?')[:40]}"
            bot.send_message(chat_id, msg)

        elif data == "dash_palace":
            try:
                palace = json.loads(open(PALACE_FILE).read()) if os.path.exists(PALACE_FILE) else {}
            except:
                palace = {}
            seasons = len(palace.get("seasonal_patterns", {}))
            brands = len(palace.get("brand_trends", {}))
            insights = len(palace.get("quarterly_insights", []))
            msg = f"🏛️ Memory Palace: {seasons} seizoenen, {brands} brands, {insights} inzichten"
            bot.send_message(chat_id, msg)

        elif data == "dash_outreach":
            try:
                out = json.loads(open(OUTREACH_FILE).read()) if os.path.exists(OUTREACH_FILE) else {}
            except:
                out = {}
            msg = f"📧 Outreach: {len(out.get('campaigns', []))} campagnes, {len(out.get('sent', []))} verstuurd"
            bot.send_message(chat_id, msg)

        elif data == "dash_skynet":
            bot.send_message(chat_id, "🛰️ Skynet cyclus starten...")
            actions = skynet_cycle()
            if actions:
                msg = "🛰️ " + "\n".join(actions[:5])
            else:
                msg = "🛰️ Skynet: alles optimaal."
            bot.send_message(chat_id, msg)

        elif data == "dash_revenue2":
            tracked = track_revenue_per_article()
            forecast = revenue_forecast()
            msg = f"💰 Revenue Radar: €{forecast.get('total_monthly', 0):.2f}/mo | {len(tracked)} artikelen"
            bot.send_message(chat_id, msg)

        elif data == "dash_authority":
            cluster_auth = calculate_cluster_authority()
            if cluster_auth:
                top = max(cluster_auth.items(), key=lambda x: x[1].get("authority_score", 0))
                msg = f"🏛️ Authority: {len(cluster_auth)} clusters | Top: {top[0]} ({top[1].get('authority_score', 0)})"
            else:
                msg = "🏛️ Authority: nog geen clusters. Gebruik /authority"
            bot.send_message(chat_id, msg)

        elif data == "dash_predict":
            write_alerts = generate_write_now_alerts()
            msg = f"🔮 Predictions: {len(write_alerts)} write-now alerts"
            if write_alerts:
                msg += f"\n⚡ Top: {write_alerts[0].get('topic', '?')[:40]}"
            bot.send_message(chat_id, msg)

        elif data == "dash_quantum":
            bot.send_message(chat_id, "🔮 Quantum Core cyclus starten...")
            actions = quantum_cycle()
            if actions:
                msg = "🔮 " + "\n".join(actions[:5])
            else:
                msg = "🔮 Quantum: alles optimaal."
            bot.send_message(chat_id, msg)

        elif data == "dash_monetize":
            opps = scan_missed_affiliate_opportunities()
            msg = f"💉 Monetize: {len(opps)} gemiste affiliate kansen"
            if opps:
                msg += f"\nTop: {opps[0]['slug'][:25]} → {opps[0]['brand']}"
            bot.send_message(chat_id, msg)

        elif data == "dash_eeat":
            eeat = score_eeat()
            if eeat:
                avg = sum(d.get("overall", 0) for d in eeat.values()) / max(len(eeat), 1)
                low = sum(1 for d in eeat.values() if d.get("overall", 0) < 40)
                msg = f"🏰 E-E-A-T: gem. {avg:.0f}/100 | {low} artikelen onder 40"
            else:
                msg = "🏰 E-E-A-T: geen data. Gebruik /eeat"
            bot.send_message(chat_id, msg)

        elif data == "dash_warroom":
            battles, victories = detect_ranking_battles()
            msg = f"⚔️ War Room: {len(battles)} battles, {len(victories)} victories"
            bot.send_message(chat_id, msg)

        elif data == "dash_omega":
            bot.send_message(chat_id, "🌀 Omega cyclus starten...")
            actions = omega_cycle()
            if actions:
                msg = "🌀 " + "\n".join(actions[:5])
            else:
                msg = "🌀 Omega: alles optimaal."
            bot.send_message(chat_id, msg)

        elif data == "act_generate":
            bot.send_message(chat_id, "📝 Gebruik /generate om een artikel te genereren")

        elif data == "act_programmatic":
            bot.send_message(chat_id, "🏭 Programmatic pagina genereren...")
            generated, total = programmatic_batch(max_pages=1)
            if generated:
                bot.send_message(chat_id, f"✅ Gegenereerd: {', '.join(generated)}")
            else:
                bot.send_message(chat_id, f"Alle {total} combinaties zijn al gemaakt!")

        elif data == "act_improve":
            bot.send_message(chat_id, "🔄 Slechtste artikel verbeteren...")
            improved = auto_improve_articles()
            if improved:
                bot.send_message(chat_id, f"✅ Verbeterd: {', '.join(improved)}")
            else:
                bot.send_message(chat_id, "Alle artikelen scoren goed!")

        elif data == "act_sprint":
            result = execute_sprint_tasks()
            bot.send_message(chat_id, f"🎯 Sprint: {result}")

        elif data == "act_domination":
            bot.send_message(chat_id, "🔥 Domination Matrix draait...")
            actions = domination_matrix_cycle()
            if actions:
                bot.send_message(chat_id, "🔥 " + "\n".join(actions))
            else:
                bot.send_message(chat_id, "Geen acties nodig.")

        elif data == "act_help":
            keyboard = build_action_keyboard()
            bot.send_message(chat_id, "⚡ Snelle Acties:", reply_markup=keyboard)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)[:200]}")


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

    return f"""📊 Victor 17.0 Omega — Status Report
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

            # 🧠 NEURAL COMMAND CENTER: self-healing elke 6 uur + dagelijkse cyclus 07:30 UTC
            if hour in [0, 6, 12, 18] and last_auto_improve != str(now.date()) + f"-heal-{hour}":
                try:
                    incidents, fixes = self_healing_check()
                    last_auto_improve = str(now.date()) + f"-heal-{hour}"
                    if incidents:
                        critical = [i for i in incidents if i.get("severity") == "critical"]
                        if critical:
                            heal_msg = "🚨 Self-Healing Alert!\n\n"
                            heal_msg += "\n".join(f"  🔴 {i['detail']}" for i in critical)
                            if fixes:
                                heal_msg += "\n\n🔧 Auto-fixes:\n" + "\n".join(f"  ✓ {f}" for f in fixes)
                            bot.send_message(ADMIN_ID, heal_msg)
                    log(f"Self-healing: {len(incidents)} incidents, {len(fixes)} fixes")
                except Exception as e:
                    log(f"Self-healing error: {e}")

            if hour == 7 and now.minute >= 30 and last_auto_improve != str(now.date()) + "-neural":
                try:
                    log("Starting neural command center cycle...")
                    neural_actions = neural_command_cycle()
                    last_auto_improve = str(now.date()) + "-neural"
                    if neural_actions:
                        neural_report = "🧠 Neural Command Center — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        neural_report += "\n".join(f"  ✅ {a}" for a in neural_actions)
                        interesting = [a for a in neural_actions if any(w in a for w in ['🚨', '🔥', '🌍', '📡', '🔍'])]
                        if interesting:
                            bot.send_message(ADMIN_ID, neural_report)
                        log(f"Neural cycle done: {len(neural_actions)} actions")
                except Exception as e:
                    log(f"Neural cycle error: {e}")

            # 🧠 HIVE MIND: dagelijkse cyclus om 08:30 UTC
            if hour == 8 and now.minute >= 30 and last_auto_improve != str(now.date()) + "-hivemind":
                try:
                    log("Starting hive mind cycle...")
                    hive_actions = hive_mind_cycle()
                    last_auto_improve = str(now.date()) + "-hivemind"
                    if hive_actions:
                        hive_report = "🧠 Hive Mind — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        hive_report += "\n".join(f"  ✅ {a}" for a in hive_actions)
                        interesting = [a for a in hive_actions if any(w in a for w in ['🏆', '🧬', '🔗', '📊'])]
                        if interesting:
                            bot.send_message(ADMIN_ID, hive_report)
                        log(f"Hive mind done: {len(hive_actions)} actions")
                except Exception as e:
                    log(f"Hive mind error: {e}")

            # Wekelijks scorecard: vrijdag 17:00 UTC
            if weekday == 4 and hour == 17 and last_auto_improve != str(now.date()) + "-scorecard":
                try:
                    scorecard = generate_scorecard()
                    bot.send_message(ADMIN_ID, scorecard)
                    leaderboard = generate_leaderboard()
                    bot.send_message(ADMIN_ID, leaderboard)
                    last_auto_improve = str(now.date()) + "-scorecard"
                    log("Weekly scorecard sent")
                except Exception as e:
                    log(f"Scorecard error: {e}")

            # 👁️ OMNISCIENCE: dagelijkse cyclus om 09:00 UTC
            if hour == 9 and last_auto_improve != str(now.date()) + "-omniscience":
                try:
                    log("Starting omniscience cycle...")
                    omni_actions = omniscience_cycle()
                    last_auto_improve = str(now.date()) + "-omniscience"
                    if omni_actions:
                        # Voeg alles toe aan digest in plaats van losse berichten
                        for action in omni_actions:
                            prio = 8 if any(w in action for w in ['🚨', '❌', 'problemen']) else 5
                            add_digest_item("omniscience", action, priority=prio)
                        log(f"Omniscience done: {len(omni_actions)} actions")
                except Exception as e:
                    log(f"Omniscience error: {e}")

            # 📋 SMART DIGEST: dagelijks om 09:30 UTC (verzamelt alles van de ochtend)
            if hour == 9 and now.minute >= 30 and last_auto_improve != str(now.date()) + "-digest":
                try:
                    digest_msg = generate_smart_digest()
                    if digest_msg:
                        bot.send_message(ADMIN_ID, digest_msg)
                        log("Daily digest sent")
                    last_auto_improve = str(now.date()) + "-digest"
                except Exception as e:
                    log(f"Digest error: {e}")

            # 🛰️ SKYNET PROTOCOL: dagelijks om 10:00 UTC (calendar + palace + dashboard + outreach)
            if hour == 10 and now.minute < 15 and last_auto_improve != str(now.date()) + "-skynet":
                try:
                    log("Starting Skynet Protocol cycle...")
                    skynet_actions = skynet_cycle()
                    last_auto_improve = str(now.date()) + "-skynet"
                    if skynet_actions:
                        skynet_report = "🛰️ Skynet Protocol — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        skynet_report += "\n".join(f"  ✅ {a}" for a in skynet_actions)
                        bot.send_message(ADMIN_ID, skynet_report)
                    log(f"Skynet cycle done: {len(skynet_actions)} actions")
                except Exception as e:
                    log(f"Skynet cycle error: {e}")

            # 🔮 QUANTUM CORE: dagelijks om 11:00 UTC (revenue + predictions + authority + social + portal)
            if hour == 11 and now.minute < 15 and last_auto_improve != str(now.date()) + "-quantum":
                try:
                    log("Starting Quantum Core cycle...")
                    quantum_actions = quantum_cycle()
                    last_auto_improve = str(now.date()) + "-quantum"
                    if quantum_actions:
                        quantum_report = "🔮 Quantum Core — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        quantum_report += "\n".join(f"  ✅ {a}" for a in quantum_actions)
                        bot.send_message(ADMIN_ID, quantum_report)
                    log(f"Quantum cycle done: {len(quantum_actions)} actions")
                except Exception as e:
                    log(f"Quantum cycle error: {e}")

            # 🌀 OMEGA PROTOCOL: dagelijks om 12:00 UTC (monetize + fortress + warroom + evolution)
            if hour == 12 and now.minute < 15 and last_auto_improve != str(now.date()) + "-omega":
                try:
                    log("Starting Omega Protocol cycle...")
                    omega_actions = omega_cycle()
                    last_auto_improve = str(now.date()) + "-omega"
                    if omega_actions:
                        omega_report = "🌀 Omega Protocol — Dagelijks\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        omega_report += "\n".join(f"  ✅ {a}" for a in omega_actions)
                        bot.send_message(ADMIN_ID, omega_report)
                    log(f"Omega cycle done: {len(omega_actions)} actions")
                except Exception as e:
                    log(f"Omega cycle error: {e}")

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
            f"🚀 Victor 17.0 Omega online!\n\n{report}"
            f"\n\n🌀 Omega: /monetize /eeat /viral /evolve /warroom /counter /omega"
            f"\n🔮 Quantum: /revenue2 /alerts /social2 /predict2 /authority /portal /quantum"
            f"\n🛰️ Skynet: /calendar /calexec /outreach /palace /dashboardv2 /api /skynet"
            f"\n👁️ Omniscience: /validate /freshness /journey /roigate /digest"
            f"\n🧠 Hive Mind: /scorecard /conversions /dna /backlinks"
            f"\n🧠 Neural: /panel /audit /trends /translate /heal"
            f"\n🔥 Domination: /domination /programmatic /schema /serp"
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
    log(f"Victor 17.0 Omega gestart — Model: {MODEL}")

    # Reset Telegram polling state — voorkomt 409 conflicts
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except Exception as e:
        log(f"Webhook reset: {e}")

    send_startup_message()

    # Start Victor API server in achtergrond
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    log(f"API server gestart op port {API_PORT}")

    # Start proactieve monitoring in achtergrond
    t = threading.Thread(target=proactive_loop, daemon=True)
    t.start()

    bot.infinity_polling(timeout=30, long_polling_timeout=20)
