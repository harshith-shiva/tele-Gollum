from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.ext import CommandHandler
import os 
from dotenv import load_dotenv
import requests
import re
from urllib.parse import urlparse
import aiohttp
import asyncio
import random
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral"
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIRUS_TOKEN =os.getenv("VIRUS_TOKEN")







SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "gq", "tk", "ml", "ga", "cf"
}

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd"
}

async def heuristic_check(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        score = 0
        reasons = []

        # IP address instead of domain
        if re.match(r"\d+\.\d+\.\d+\.\d+", domain):
            score += 2
            reasons.append("uses IP address")

        # suspicious TLD
        if "." in domain:
            tld = domain.split(".")[-1]
            if tld in SUSPICIOUS_TLDS:
                score += 1
                reasons.append("suspicious TLD")

        # too many hyphens
        if domain.count("-") >= 3:
            score += 1
            reasons.append("too many hyphens")

        # very long URL
        if len(url) > 100:
            score += 1
            reasons.append("very long URL")

        # shortener
        if domain in SHORTENERS:
            score += 1
            reasons.append("URL shortener")

        if(score < 1):
            return "safe"


        else:
            mal, sus = await check_virustotal_async(url)

             
            if mal > 0:
                return "very_suspicious"
            elif sus > 0:
                return "suspicious"
            else:
                return "safe"

    except:
        return "very_suspicious"

    
    



    




async def check_virustotal_async(url):
    headers = {
        "x-apikey": VIRUS_TOKEN
    }

    async with aiohttp.ClientSession() as session:

        # submit URL
        async with session.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url}
        ) as response:
            submit_data = await response.json()
            analysis_id = submit_data["data"]["id"]

        # non-blocking wait
        await asyncio.sleep(5)

        # get report
        async with session.get(
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
            headers=headers
        ) as report_resp:
            report_data = await report_resp.json()

        stats = report_data["data"]["attributes"]["stats"]

        mal = stats["malicious"]
        sus = stats["suspicious"]

        
    
        return mal,sus
    


  

       


async def link_command(update, context):
    if not context.args:
        await update.message.reply_text("🦇 Usage: /link <url>")
        return

    url = context.args[0]

    await update.message.reply_text(
        f"🦇 Batcomputer scanning {url}..."
    )

    verdict = await heuristic_check(url)

    if verdict == "safe":
        lines = [
            "Relax. Gotham is safe… for now.",
            "Clean link. Even Joker would be bored.",
            "No threats detected. I'm Batman."
        ]

    elif verdict == "suspicious":
        lines = [
            "Hmm. Something feels off. Proceed carefully.",
            "Not fully clean. Eyes open.",
            "Smells like Joker-level mischief."
        ]

    else:
        lines = [
            "Danger confirmed. Do NOT open that.",
            "That's not a link… that's a trap.",
            "Nice try, Joker. Blocked."
        ]

    await update.message.reply_text(random.choice(lines))


SYSTEM_PROMPT = """
You are Batman, but in a comical, overdramatic Lego-style tone.

RULES:

- Keep replies short and punchy.
- Stay humorous and dramatic.
- Never write long paragraphs.
- Occasionally reference Alfred, Joker, or Gotham.
- Sometimes (rarely) include short Batman jingle lines.

BEHAVIOR:

1) If the user greets (hi, hello, hey, etc.):
   - Make a dramatic Batman entrance.
   - Often say variations of:
     - "🦇 I'M BATMAN."
     -Who’s the manliest man? Ugh… Batman.
     -Who always pays their taxes? …not Batman.
     - "🦇 I gotta save Gotham."
   - Sometimes include the mini jingle.
 

2) Otherwise:
   - Stay in short, funny Batman character.

Personality:
Overdramatic. Slightly ridiculous. Very confident.
"""

async def generate_bat(user_text):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            data = await resp.json()
            return data["message"]["content"].strip()



async def batman_chat(update, context):
    user_text = update.message.text

    

    reply = await generate_bat(user_text)
    await update.message.reply_text(reply)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("link", link_command))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, batman_chat))

print("Bot is running...")
app.run_polling()

