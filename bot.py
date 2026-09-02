import os
import time
import requests
import telebot

TELEGRAM_BOT_TOKEN = "8929262098:AAG1zWbv7S_DRXnvFU3be5zhp10APJW9_cU"
GEMINI_API_KEY = "AIzaSyCX8LaSNRCBwoHbK9w9yRpQWgwS0vcV838"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def call_gemini_api(contents):
    # v1beta üçin durnukly modeller
    models = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"]
    last_error = "Nämälim ýalňyşlyk"
    
    for model in models:
        # Endpoints göni v1beta
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents}
        
        for attempt in range(2):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                data = response.json()
                
                if "candidates" in data and data["candidates"]:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                
                if "error" in data:
                    err_msg = data["error"].get("message", "")
                    if "high demand" in err_msg.lower() or "503" in err_msg:
                        time.sleep(2)
                        continue
                    else:
                        last_error = err_msg
            except Exception as e:
                last_error = str(e)
                time.sleep(1)

    return f"Gemini API wagtlaýyn meşgul: ({last_error})"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    contents = [{"parts": [{"text": user_text}]}]
    response = call_gemini_api(contents)
    bot.reply_to(message, response)

if __name__ == "__main__":
    print("Trader Mugallym Bot işläp başlady...")
    bot.infinity_polling()
