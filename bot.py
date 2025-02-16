import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"
CHANNELS = ["@channel1", "@channel2", "@channel3"]  # Kanal usernames

bot = telebot.TeleBot(TOKEN)
movies = {
    "15": "🎬 Kino: Avengers: Endgame",
    "22": "🎬 Kino: Titanic",
    "33": "🎬 Kino: Interstellar"
}

def check_subscription(user_id):
    for channel in CHANNELS:
        status = bot.get_chat_member(channel, user_id).status
        if status not in ['member', 'administrator', 'creator']:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    markup = InlineKeyboardMarkup()
    for channel in CHANNELS:
        markup.add(InlineKeyboardButton(f"🔗 Kanalga o'tish", url=f"https://t.me/{channel[1:]}"))
    markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
    bot.send_message(user_id, "🔹 Iltimos, quyidagi kanallarga obuna bo‘ling va tasdiqlash tugmasini bosing:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    user_id = call.message.chat.id
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino kodini kiriting:")
    else:
        bot.send_message(user_id, "❌ Siz hali barcha kanallarga obuna bo‘lmadingiz! Avval ularga qo‘shiling.")

@bot.message_handler(func=lambda message: True)
def send_movie(message):
    movie_code = message.text.strip()
    response = movies.get(movie_code, "❌ Bunday kod topilmadi.")
    bot.send_message(message.chat.id, response)

bot.polling(none_stop=True)
