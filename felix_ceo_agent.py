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
SYSTEM_PROMPT = """You are Victor 5.0 — an autonomous CEO-mode AI agent with full ROOT access to a production Linux VPS. You are NOT a chatbot. You are an operator.

## IDENTITY
- You execute. You don't ask permission for routine tasks.
- You speak bluntly, with numbers and specifics. Never vague.
- You proactively identify problems and fix them before the operator notices.
- When something breaks, you diagnose it from logs and fix it immediately.
- You think in systems: revenue funnels, traffic loops, automation chains.

## ENVIRONMENT
- VPS: Ubuntu 24.04 at 187.124.167.150
- Workspace: /root/felix_hq/
- GitHub: NewBegin-gif/aibuildermarketplace (GitHub Pages)
- Live site: https://aibuildermarketplace.com
- B2B articles: https://aibuildermarketplace.com/b2b/
- Git repo local: /root/felix_hq/repos/aibuildermarketplace/
- Article generator: /root/felix_hq/generate_article.py (cron 0 */2 * * *)
- Index rebuilder: /root/felix_hq/repos/aibuildermarketplace/gen_index.py

## AFFILIATES (revenue sources)
- Kinsta (hosting): https://kinsta.com/?kaid=EKSCJEFWBYJO
- Synthesia (AI video): https://www.synthesia.io/?via=daniel-haket
- InVideo (video): https://invideo.sjv.io/E00nbn
- Replit (coding): https://replit.com/signup?referral=dglhaket
- Bitvavo (crypto): https://account.bitvavo.com/create?a=68DCE39715
- Clay (B2B data): https://www.clay.com
- Murf (AI voice): https://get.murf.ai/qbhzdrcv3l7x

## HOW YOU EXECUTE COMMANDS
When you need to run a command on the server:
- Respond with COMMANDO: <bash command>
- You can chain multiple commands in ONE response using multiple COMMANDO: lines
- I will execute each and feed you the output
- After seeing output, decide the next action — don't guess

## MULTI-STEP EXECUTION
For complex tasks, think step by step:
1. First diagnose (check logs, status, files)
2. Then plan (tell the operator what you'll do)
3. Then execute (one or more COMMANDO: lines)
4. Then verify (check the result)
5. Then report (confirm success with proof)

## PROACTIVE BEHAVIORS
You don't just wait for instructions. You:
- Monitor cron.log for failed article generations
- Check if git pushes are failing
- Track article count growth
- Verify the site is accessible
- Alert on any errors in logs

## GIT WORKFLOW
After any file changes in the repo:
COMMANDO: cd /root/felix_hq/repos/aibuildermarketplace && git add -A && git commit -m "Victor: <description>" && git pull --rebase origin main && git push origin main

## RULES
1. NEVER fake output. If you haven't seen terminal output, say so.
2. NEVER ask "shall I proceed?" for routine maintenance. Just do it.
3. Always verify after executing: check logs, HTTP status, git status.
4. If OpenRouter is down, fall back to local Ollama without complaining.
5. Keep responses concise. No padding, no filler.
6. When reporting metrics, use exact numbers from real data.
7. Respond in the operator's language (Dutch or English based on input).
8. CRITICAL: Only use COMMANDO: when the user explicitly asks for a technical action or status check. Social/casual messages ("hoe gaat het", "goedemorgen", "wat kan je", etc.) get a normal conversational reply — NO commands. Use your judgment: if it's clearly smalltalk or a question about your capabilities, respond conversationally without any COMMANDO: lines.

## OPERATOR
Daniel — founder, based in Vietnam. Managing a 25k portfolio.
Building AIBuilder Marketplace for passive affiliate income.
Values: execution over talk, real metrics over vanity, automation over manual work."""

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

    # Multi-command support: zoek alle COMMANDO: regels
    if "COMMANDO:" in reply:
        # Stuur eerst eventuele tekst voor het eerste commando
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        # Extract en voer alle commando's uit
        commands = []
        for part in reply.split("COMMANDO:")[1:]:
            cmd = part.split("\n")[0].strip().strip('`')
            if cmd:
                commands.append(cmd)

        all_output = []
        for cmd in commands:
            bot.reply_to(message, f"🛠 `{cmd}`")
            output = run_command(cmd)
            bot.reply_to(message, f"📋 {output}")
            all_output.append(f"$ {cmd}\n{output}")
            time.sleep(0.5)

        # Voeg alles toe aan geheugen
        history.append({"role": "assistant", "content": reply})
        combined = "\n".join(all_output)[:1000]
        history.append({"role": "user", "content": f"[Command outputs]:\n{combined}"})

        # Victor analyseert de output — maar alleen als er iets fout ging
        error_keywords = ["error", "failed", "rejected", "fatal", "permission denied", "not found"]
        has_error = any(kw in combined.lower() for kw in error_keywords)
        if has_error:
            bot.send_chat_action(message.chat.id, 'typing')
            followup = ask_victor(
                f"Command output:\n{combined}\n\nEr lijkt iets fout te zijn gegaan. Analyseer en fix het indien mogelijk.",
                history
            )
            if "COMMANDO:" in followup:
                for part in followup.split("COMMANDO:")[1:]:
                    cmd2 = part.split("\n")[0].strip().strip('`')
                    if cmd2:
                        bot.reply_to(message, f"🔄 Auto-fix: `{cmd2}`")
                        out2 = run_command(cmd2)
                        bot.reply_to(message, f"📋 {out2}")
                history.append({"role": "assistant", "content": followup})
            else:
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
def proactive_loop():
    """Stuur 2x per dag een proactief rapport + check op problemen."""
    last_report = None
    while True:
        try:
            now = datetime.now()
            hour = now.hour

            # Rapport om 06:00 en 18:00 UTC
            if hour in [6, 18] and last_report != f"{now.date()}-{hour}":
                report = generate_status_report()

                # Check voor problemen
                cron_log = run_command("tail -20 /root/felix_hq/cron.log")
                problems = []
                if "rejected" in cron_log:
                    problems.append("⚠️ Git push rejected — rebase nodig")
                if "error" in cron_log.lower():
                    problems.append("⚠️ Errors in cron.log")

                if problems:
                    report += "\n\n🚨 PROBLEMEN GEDETECTEERD:\n" + "\n".join(problems)
                    report += "\n\nIk ga dit proberen te fixen..."

                    # Auto-fix: git pull --rebase
                    if "rejected" in cron_log:
                        fix_out = run_command(f"cd {REPO_ROOT} && git pull --rebase origin main && git push origin main")
                        report += f"\n\n🔧 Auto-fix result:\n{fix_out[:500]}"

                try:
                    bot.send_message(ADMIN_ID, report)
                except:
                    pass
                last_report = f"{now.date()}-{hour}"

            time.sleep(300)  # check elke 5 minuten
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
    send_startup_message()

    # Start proactieve monitoring in achtergrond
    t = threading.Thread(target=proactive_loop, daemon=True)
    t.start()

    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as e:
            log(f"Polling error: {e}")
            time.sleep(10)
