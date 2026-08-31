import logging
import requests
import base64
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.request import HTTPXRequest

# Tokenler Environment Variables-dan alynýar
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN tapylmady!")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY tapylmady!")

# SYSTEM PROMPT
SYSTEM_PROMPT = """
Sen Balkana Trading öwretmek üçin ýasalan hünärmen Trader Mugallym.
Seniň adyň: Trader Mugallym.

ESASY BILIM BINÝADY:
1. Technical Analysis, Price Action, Smart Money Concepts (SMC/ICT)
2. Risk Management we Grafik Analiz.

DÜZGÜNLER:
1. Diňe Trading we Grafik analiz barada jogap ber.
2. Ähli jogaplaryňy Türkmen dilinde ber.
"""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# HEALTH CHECK SERVER (Render / FPS.ms üçin)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Trader Mugallym Bot: ACTIVE")

    def log_message(self, format, *args):
        return

def run_health_check_server():
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# GEMINI API CALL (Model Ýalňyşlyklaryny Dolydan Çözýän Awto-Fallback)
def call_gemini_api(contents):
    # API-da 100% işleýän durnukly modelleriň sanawy
    models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    last_error = "Nämälim ýalňyşlyk"

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            data = response.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            if "error" in data:
                last_error = data["error"].get("message", str(data["error"]))
        except Exception as error:
            last_error = str(error)

    return f"Gemini API ýalňyşlygy: {last_error}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = "Salam! Men Trader Mugallym. 📈\n\nBalkana trading öwretmek üçin ýasaldym.\n\nSMC/ICT we Grafik analizi boýunça soraglaryňyzy berip ýa-da grafik suratlaryny iberip bilersiňiz!"
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    contents = [{"parts": [{"text": SYSTEM_PROMPT}, {"text": f"Ulanyjynyň soragy:\n{user_text}"}]}]
    reply = call_gemini_api(contents)
    await update.message.reply_text(reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Grafigiňizi aldym 📊\nAnaliz edýärin...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        base64_image = base64.b64encode(photo_bytes).decode("utf-8")
        user_caption = update.message.caption if update.message.caption else "Bu trading grafigini doly analiz et."
        contents = [{
            "parts": [
                {"text": SYSTEM_PROMPT},
                {"text": user_caption},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }]
        reply = call_gemini_api(contents)
        await update.message.reply_text(reply)
    except Exception as error:
        logging.exception(error)
        await update.message.reply_text("Ulgamda ýalňyşlyk boldy.")

if __name__ == "__main__":
    threading.Thread(target=run_health_check_server, daemon=True).start()
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=60.0)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Trader Mugallym Bot işläp başlady!")
    app.run_polling()

