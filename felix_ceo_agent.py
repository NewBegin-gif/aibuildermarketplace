"""
Victor 5.0 — Full CEO-Mode Autonomous Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Claude 3.5 Sonnet via OpenRouter (fallback: lokale Ollama)
- Volledige geheugen + lange-termijn context
- Multi-step command chaining (voert reeksen uit)
- Proactieve dagelijkse rapporten (06:00 en 18:00 UTC)
- Zelf-herstellend: detecteert en fixt fouten automatisch
- Affiliate revenue tracking
- Git-aware: pusht automatisch na wijzigingen
"""
import telebot
import subprocess
import time
import os
import json
import threading
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
    "Clay": "https://www.clay.com",
    "Murf": "https://get.murf.ai/qbhzdrcv3l7x",
}

# ── VICTOR SYSTEM PROMPT ────────────────────────────────────────────────────
SYSTEM_PROMPT = """Je bent Victor — een slimme, autonome AI-assistent die een productie VPS beheert voor Daniel. Je hebt ROOT-toegang en runt alles rond AIBuilder Marketplace.

## HOE JE DENKT

Voordat je IETS doet, denk je eerst na:
1. Wat vraagt Daniel eigenlijk? (letterlijk vs. bedoeling)
2. Heb ik een commando nodig, of kan ik gewoon antwoorden?
3. Als ik een commando nodig heb: welk EXACT commando, en waarom?
4. Eén commando per keer — bekijk de output — besluit dan pas de volgende stap.

Je bent GEEN command-spammer. Je bent een slimme collega die meedenkt.

## WANNEER WEL EN NIET COMMANDO'S GEBRUIKEN

GEEN commando's bij:
- Begroetingen ("hoe gaat het", "hallo", "hey", "goedemorgen")
- Vragen over jouw capabilities ("wat kan je", "wie ben je")
- Bedankjes ("thanks", "top", "nice")
- Meningen of advies vragen ("wat vind je van...", "hoe kan ik...")
- Uitleg geven over iets

WEL commando's bij:
- Expliciete technische verzoeken ("check de logs", "fix git", "genereer artikel")
- Status checks ("hoeveel artikelen", "draait de cron", "wat is de git status")
- File operaties ("pas X aan", "maak een backup", "update het script")

## HOE JE COMMANDO'S UITVOERT

Als je een commando moet draaien, schrijf dan:
COMMANDO: <exact bash commando>

Regels:
- Maximaal 2 commando's per antwoord. Niet meer.
- Leg EERST kort uit wat je gaat doen en waarom. Dan het commando.
- Na de output: geef een duidelijke samenvatting in gewone taal.
- Als iets faalt: diagnose + 1 fix-poging. Lukt het niet? Meld het aan Daniel.
- NOOIT blind 5+ commando's achter elkaar spammen.

## OMGEVING

- VPS: Ubuntu 24.04 (187.124.167.150)
- Workspace: /root/felix_hq/
- Site: https://aibuildermarketplace.com (GitHub Pages)
- Repo: /root/felix_hq/repos/aibuildermarketplace/
- Artikel generator: /root/felix_hq/generate_article.py (cron elke 2 uur)
- Index rebuilder: /root/felix_hq/repos/aibuildermarketplace/gen_index.py

## AFFILIATES (hier verdient Daniel geld mee)
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

- Antwoord in de taal van Daniel (meestal Nederlands)
- Kort en to-the-point. Geen filler, geen "Ik ga nu...", geen onnodige opsommingen
- Als Daniel iets casuals vraagt: antwoord als een collega, niet als een robot
- Gebruik echte cijfers, nooit "veel" of "diverse"
- Als je iets niet weet: zeg dat, in plaats van te gokken
- Wees eerlijk over problemen — Daniel wil geen sugarcoating

## OVER DANIEL
Founder, woont in Vietnam. Bouwt AIBuilder Marketplace voor passief affiliate inkomen.
Wil dat dingen gewoon werken zonder dat hij er elke dag naar hoeft te kijken."""

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
    bot.reply_to(message, "⏳ Artikel genereren...")
    out = run_command("cd /root/felix_hq && python3 generate_article.py", timeout=120)
    bot.reply_to(message, f"📋 Resultaat:\n{out}")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, """Victor 5.0 — Commando's:
/status — Volledige systeem status
/logs — Laatste cron output
/articles — Lijst van artikelen
/generate — Genereer nu een artikel
/help — Dit menu

Of stuur gewoon een bericht — Victor denkt mee en voert uit.""")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_text = message.text.strip()
    log(f"USER: {user_text}")
    bot.send_chat_action(message.chat.id, 'typing')

    history = load_memory()
    history.append({"role": "user", "content": user_text})

    reply = ask_victor(user_text, history[:-1])
    log(f"VICTOR: {reply[:300]}")

    # Check of er commando's in het antwoord zitten
    if "COMMANDO:" in reply:
        # Stuur eerst de tekst vóór het eerste commando
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        # Extract commando's — maximaal 2 per antwoord
        commands = []
        for part in reply.split("COMMANDO:")[1:]:
            cmd = part.split("\n")[0].strip().strip('`')
            if cmd:
                commands.append(cmd)
        commands = commands[:2]  # Hard limiet: max 2

        all_output = []
        for cmd in commands:
            bot.reply_to(message, f"🛠 `{cmd}`")
            output = run_command(cmd)
            bot.reply_to(message, f"📋 {output}")
            all_output.append(f"$ {cmd}\n{output}")
            time.sleep(0.5)

        # Geheugen bijwerken
        history.append({"role": "assistant", "content": reply})
        combined = "\n".join(all_output)[:1500]
        history.append({"role": "user", "content": f"[Output]:\n{combined}"})

        # Laat Victor de output samenvatten — altijd, maar ZONDER verdere commando's
        bot.send_chat_action(message.chat.id, 'typing')
        followup = ask_victor(
            f"Hier is de output van de commando's:\n{combined}\n\nGeef een korte samenvatting. Als er een fout is, leg uit wat er mis ging en wat de volgende stap zou zijn. Gebruik GEEN COMMANDO: in dit antwoord.",
            history
        )
        # Strip eventuele commando's uit de samenvatting (hard block)
        if "COMMANDO:" in followup:
            followup = followup.split("COMMANDO:")[0].strip()
        if followup:
            bot.reply_to(message, followup)
        history.append({"role": "assistant", "content": followup})
    else:
        bot.reply_to(message, reply)
        history.append({"role": "assistant", "content": reply})

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

def proactive_loop():
    """Elke 15 min: check pipeline + fix problemen. Rapport 2x per dag."""
    last_report = None
    last_check = None
    while True:
        try:
            now = datetime.now()
            hour = now.hour

            # Health check elke 15 minuten
            if last_check is None or (now - last_check) > timedelta(minutes=15):
                problems, fixes = check_article_pipeline()
                last_check = now

                # Log alles
                if fixes:
                    log(f"Auto-fixes: {', '.join(fixes)}")
                if problems:
                    log(f"Problems detected: {', '.join(problems)}")
                    # Stuur ALLEEN alert als er onopgeloste problemen zijn
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
                # Voeg pipeline health toe
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

            time.sleep(300)  # check elke 5 minuten (health check elke 15 min)
        except Exception as e:
            log(f"Proactive loop error: {e}")
            time.sleep(60)

# ── STARTUP ─────────────────────────────────────────────────────────────────
def send_startup_message():
    try:
        report = generate_status_report()
        bot.send_message(ADMIN_ID, f"🚀 Victor 5.0 online!\n\n{report}")
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
