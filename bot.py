import os
import requests
import telebot

# API AÇARLARY WE TOKENLER
TELEGRAM_BOT_TOKEN = "8929262098:AAG1zWbv7S_DRXnvFU3be5zhp10APJW9_cU"
GEMINI_API_KEY = "AIzaSyCX8LaSNRCBwoHbK9w9yRpQWgwS0vcV838"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# GEMINI API CALL (Diňe goldanýan gemini-3.6-flash)
def call_gemini_api(contents):
    models = ["gemini-3.6-flash"]
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
    
