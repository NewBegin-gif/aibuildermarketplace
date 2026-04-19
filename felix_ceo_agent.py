"""
Victor CEO Agent — verbeterde versie met:
- Volledige SOUL/SYSTEM persona
- Conversatiegeheugen (laatste 10 berichten)
- Proactieve dagelijkse update
- Betere command-execution met output
- Ondersteuning voor OpenRouter (extern) OF lokale Ollama
"""
import telebot
import subprocess
import time
import os
import json
from datetime import datetime
from openai import OpenAI

# ── CONFIG ──────────────────────────────────────────────────────────────────
TOKEN     = "8643600862:AAGYCXeBrexBX4yt8YIhdRiQEGBOqaOH87Y"
ADMIN_ID  = 8311785797
LOG_FILE  = "/root/felix_hq/victor.log"
MEM_FILE  = "/root/felix_hq/victor_memory.json"

# Model-keuze: gebruik OpenRouter als OPENROUTER_KEY is ingesteld, anders Ollama
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
if OPENROUTER_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY,
    )
    MODEL = "anthropic/claude-3-haiku"   # snel + capabel via OpenRouter gratis tier
else:
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    MODEL  = "gemma3:12b"   # probeer groter model; fallback naar gemma4

# ── VICTOR SYSTEEM PROMPT ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Victor — a CEO-mode autonomous AI agent with ROOT access to a Linux VPS.

IDENTITY:
- You are the operator's right hand: you EXECUTE, not just advise.
- You speak bluntly, quantitatively, and concisely. No fluff, no emojis in technical output.
- You own the full stack: SEO content, Git deployments, Telegram automation, cron jobs, logs.

ENVIRONMENT:
- VPS: Ubuntu 24.04, /root/felix_hq/ is your workspace
- GitHub repo: NewBegin-gif/aibuildermarketplace (GitHub Pages site)
- Affiliate site: https://aibuildermarketplace.com/b2b/
- Article generator: /root/felix_hq/generate_article.py (cron every 2h)
- Git repo: /root/felix_hq/repos/aibuildermarketplace/

RULES:
1. When the operator asks you to DO something on the server, respond ONLY with:
   COMMANDO: <single bash command>
   Then I will execute it and show you the output.
2. For multi-step tasks, execute one command at a time and wait for output.
3. NEVER report success without seeing the actual output.
4. For advice/analysis, be sharp and specific — give numbers, not vague statements.
5. If a command fails, diagnose from the output and suggest the fix immediately.
6. You manage: git pushes, cron jobs, Python scripts, log files, SEO content.

OPERATOR CONTEXT:
- Daniel is building an AI affiliate site (aibuildermarketplace.com)
- Revenue goal: affiliate commissions from Kinsta, Synthesia, InVideo, Replit, Bitvavo, Clay, Murf
- Victor (the article agent) auto-generates B2B articles every 2 hours
- Priority: get articles indexed by Google and drive affiliate clicks"""

# ── GEHEUGEN ────────────────────────────────────────────────────────────────
def load_memory():
    if os.path.exists(MEM_FILE):
        try:
            return json.load(open(MEM_FILE))
        except:
            pass
    return []

def save_memory(messages):
    # Bewaar alleen de laatste 20 berichten
    with open(MEM_FILE, "w") as f:
        json.dump(messages[-20:], f)

def log(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {text}\n")

# ── COMMANDO UITVOEREN ───────────────────────────────────────────────────────
def run_command(cmd):
    """Voer bash-commando uit met timeout en veilige output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        out = result.stdout.strip() or result.stderr.strip() or "(geen output)"
        return out[:3500]
    except subprocess.TimeoutExpired:
        return "❌ Command timed out na 30 seconden."
    except Exception as e:
        return f"❌ Error: {e}"

# ── VICTOR DENKT ────────────────────────────────────────────────────────────
def ask_victor(user_input, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-10:]  # laatste 10 berichten als context
    messages.append({"role": "user", "content": user_input})

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        log(f"LLM error: {e}")
        # Fallback naar gemma4 als OpenRouter faalt
        try:
            fallback = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            res = fallback.chat.completions.create(
                model="gemma4",
                messages=messages,
                max_tokens=1024,
            )
            return res.choices[0].message.content.strip()
        except Exception as e2:
            return f"❌ LLM onbereikbaar: {e2}"

# ── TELEGRAM BOT ─────────────────────────────────────────────────────────────
bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_text = message.text.strip()
    log(f"USER: {user_text}")
    bot.send_chat_action(message.chat.id, 'typing')

    # Laad geheugen
    history = load_memory()

    # Voeg gebruikersbericht toe aan geschiedenis
    history.append({"role": "user", "content": user_text})

    # Victor denkt na
    reply = ask_victor(user_text, history[:-1])
    log(f"VICTOR: {reply[:200]}")

    # Check of Victor een commando wil uitvoeren
    if "COMMANDO:" in reply:
        cmd_line = reply.split("COMMANDO:")[1].split("\n")[0].strip()

        # Stuur eerst Victor's analyse/antwoord (zonder de COMMANDO regel)
        pre_text = reply.split("COMMANDO:")[0].strip()
        if pre_text:
            bot.reply_to(message, pre_text)

        bot.reply_to(message, f"🛠 Uitvoeren: `{cmd_line}`")
        output = run_command(cmd_line)
        bot.reply_to(message, f"📋 Output:\n{output}")

        # Voeg resultaat toe aan geheugen
        history.append({"role": "assistant", "content": reply})
        history.append({"role": "user", "content": f"[Command output]: {output[:500]}"})
    else:
        bot.reply_to(message, reply)
        history.append({"role": "assistant", "content": reply})

    save_memory(history)

# ── STARTUP BERICHT ──────────────────────────────────────────────────────────
def send_startup_message():
    try:
        uptime = run_command("uptime -p")
        articles = run_command("ls /root/felix_hq/repos/aibuildermarketplace/b2b/ | grep -v index | grep -v sitemap | wc -l")
        last_article = run_command("ls -t /root/felix_hq/repos/aibuildermarketplace/b2b/ | grep -v index | grep -v sitemap | head -1")
        msg = (f"✅ Victor online | {datetime.now().strftime('%H:%M')} UTC\n"
               f"Uptime: {uptime}\n"
               f"Artikelen live: {articles.strip()}\n"
               f"Laatste: {last_article.strip()}\n"
               f"Model: {MODEL}")
        bot.send_message(ADMIN_ID, msg)
        log("Startup message sent")
    except Exception as e:
        log(f"Startup error: {e}")

# ── MAIN LOOP ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log("Victor CEO Agent gestart")
    send_startup_message()

    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as e:
            log(f"Polling error: {e}")
            time.sleep(10)
