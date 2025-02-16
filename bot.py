import telebot
from flask import Flask, request
import os

# 🔹 Muhit o'zgaruvchilaridan TOKEN olish
TOKEN = os.getenv("BOT_TOKEN")  # ❌ To‘g‘ridan-to‘g‘ri yozish o‘rniga muhit o‘zgaruvchisidan olamiz
HEROKU_APP_NAME = "sunnat-telegram-bot"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram bot server ishlayapti!"

@app.route(f'/{TOKEN}', methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Salom! Ushbu bot kinolarni kod orqali yuboradi. \n\n🔢 Kodni kiriting:")

@bot.message_handler(func=lambda message: True)
def send_movie(message):
    movie_code = message.text.strip()
    movies = {
        "15": "🎬 Kino: Avengers: Endgame",
        "22": "🎬 Kino: Titanic",
        "33": "🎬 Kino: Interstellar"
    }
    response = movies.get(movie_code, "❌ Bunday kod topilmadi.")
    bot.send_message(message.chat.id, response)

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
