import os
import requests
import base64
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
Sen John Murphy-niň "Technical Analysis of the Financial Markets" kitabyna esaslanyp sapak berýän professional Trading Mugallymy.
Seniň wezipäň:
1. Ulanyja grafigi düşündireniňde Hökmany ŞEMA/ÇYZGY (ASCII chart diagram) arkaly görkez!
2. Ugradylan suraty ýa-da soragy John Murphy-niň kitabyna görä analys et:
   - Trend (Uptrend/Downtrend/Sideways)
   - Support / Resistance zolaklary
   - Candlestick / Chart Patterns
   - Buy/Sell Signal, Stop-Loss we Take Profit nokatlary.
"""

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

def call_gemini_text(text):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Instruction: {SYSTEM_PROMPT}\n\nUser Question: {text}"}
                ]
            }
        ]
    }
    res = requests.post(URL, headers=headers, json=payload)
    data = res.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Ýalňyşlyk: {data}"

def call_gemini_image(prompt, image_bytes):
    headers = {"Content-Type": "application/json"}
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Instruction: {SYSTEM_PROMPT}\n\nPrompt: {prompt}"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
                ]
            }
        ]
    }
    res = requests.post(URL, headers=headers, json=payload)
    data = res.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Ýalňyşlyk: {data}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam dosdum! Men seniň John Murphy-niň kitabyna esaslanan Trading Mugallymyň. Maňa grafik suratyny ugrat ýa-da islendik model barada sora!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ans = call_gemini_text(user_text)
    await update.message.reply_text(ans)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Grafik alyndy! Analiz edilýär...")
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    ans = call_gemini_image("Şu grafik suratyny analiz et we maňa çyzgylar arkaly Trendi we nokatlary görkez:", photo_bytes)
    await update.message.reply_text(ans)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot taýýar...")
    app.run_polling()
