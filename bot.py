import os
import requests
import telebot

# Environment-den tokenleri almak
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN tapylmady!")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY tapylmady!")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# GEMINI API CALL
def call_gemini_api(contents):
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    contents = [{"parts": [{"text": user_text}]}]
    response = call_gemini_api(contents)
    bot.reply_to(message, response)

if __name__ == "__main__":
    print("Trader Mugallym Bot işläp başlady...")
    bot.infinity_polling()
    
