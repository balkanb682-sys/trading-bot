import os
import telebot
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = "8929262098:AAG1zWbv7S_DRXnvFU3be5zhp10APJW9_cU"
GEMINI_API_KEY = "AIzaSyCX8LaSNRCBwoHbK9w9yRpQWgwS0vcV838"

# Google Gemini SDK sazlamasy
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ýalňyşlyk döräp bildi: {str(e)}")

if __name__ == "__main__":
    print("Trader Mugallym Bot (gemini-1.5-flash) işläp başlady...")
    bot.infinity_polling()
    
