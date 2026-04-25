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
from datetime import datetime, timedelta
from openai import OpenAI

# ── CONFIG ──────────────────────────────────────────────────────────────────
TOKEN     = "8643600862:AAGYCXeBrexBX4yt8YIhdRiQEGBOqaOH87Y"
ADMIN_ID  = 8311785797
LOG_FILE  = "/root/felix_hq/victor.log"
MEM_FILE  = "/root/felix_hq/victor_memory.json"
LONG_MEM  = "/root/felix_hq/victor_long_memory.json"
REPO_ROOT = "/root/felix_hq/repos/aibuildermarketplace"

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

def load_long_memory():
    if os.path.exists(LONG_MEM):
        try:
            return json.load(open(LONG_MEM))
        except:
            pass
    return {"facts": [], "decisions": [], "errors": []}

def save_long_memory(mem):
    mem["facts"] = mem["facts"][-50:]
    mem["decisions"] = mem["decisions"][-30:]
    mem["errors"] = mem["errors"][-20:]
    with open(LONG_MEM, "w") as f:
        json.dump(mem, f, indent=2)

def extract_learnings(user_text, victor_reply):
    """Sla belangrijke feiten en beslissingen op in lange-termijn geheugen."""
    long_mem = load_long_memory()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    keywords = ["onthoud", "remember", "belangrijk", "important", "besluit", "decision",
                "voortaan", "from now on", "altijd", "always", "nooit", "never"]
    if any(kw in user_text.lower() for kw in keywords):
        long_mem["facts"].append({"time": ts, "fact": user_text})
        save_long_memory(long_mem)

    if "error" in victor_reply.lower() or "failed" in victor_reply.lower():
        long_mem["errors"].append({"time": ts, "error": victor_reply[:200]})
        save_long_memory(long_mem)

def get_long_memory_context():
    """Geeft lange-termijn context als string voor het systeem prompt."""
    long_mem = load_long_memory()
    parts = []
    if long_mem["facts"]:
        parts.append("OPERATOR FACTS:\n" + "\n".join(f"- {f['fact']}" for f in long_mem["facts"][-10:]))
    if long_mem["errors"]:
        parts.append("RECENT ERRORS:\n" + "\n".join(f"- [{e['time']}] {e['error']}" for e in long_mem["errors"][-5:]))
    return "\n\n".join(parts) if parts else ""

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

@bot.message_handler(commands=['revenue'])
def cmd_revenue(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "💰 Revenue check...")
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
    # Handle als normaal bericht (kan commando's bevatten)
    handle_victor_reply(message, reply, history)

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

@bot.message_handler(commands=['help'])
def cmd_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, """Victor Ultra — Commando's:

📊 Monitoring:
/status — Systeem status
/logs — Cron output
/uptime — Website bereikbaarheid
/articles — Artikel overzicht

🔍 Analyse:
/seo — SEO gezondheidscheck
/revenue — Affiliate link rapport
/linkcheck — Test alle affiliate URLs
/quality — Artikelkwaliteit analyse
/strategy — AI strategisch advies

🚀 Actie:
/generate — Genereer een artikel
/improve — Verbeter het slechtste artikel
/optimize — Voeg interne links toe
/fix <probleem> — Los op (stopt niet tot het werkt)
/write <taak> — Schrijf code of scripts

Of stuur gewoon een bericht — ik denk mee en pak door.""")

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
    MAX_ROUNDS = 8  # veiligheidsgrens
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

    return f"""📊 Victor 5.0 — Status Report
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
    """Elke 15 min: check pipeline + fix problemen. Rapport 2x per dag + wekelijks strategie."""
    last_report = None
    last_check = None
    last_weekly = None
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

                try:
                    bot.send_message(ADMIN_ID, report)
                except:
                    pass
                last_report = f"{now.date()}-{hour}"

            # Wekelijks strategierapport: maandag 08:00 UTC
            if weekday == 0 and hour == 8 and last_weekly != str(now.date()):
                try:
                    strategy = generate_weekly_strategy()
                    bot.send_message(ADMIN_ID, f"📈 Wekelijks Strategie Rapport\n━━━━━━━━━━━━━━━━━━━━━\n\n{strategy}")
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
        bot.send_message(ADMIN_ID, f"🚀 Victor Ultra online!\n\n{report}\n\nNieuw: /fix /write /seo /revenue /strategy")
        log("Startup message sent")
    except Exception as e:
        log(f"Startup error: {e}")

# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log(f"Victor 5.0 gestart — Model: {MODEL}")

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
