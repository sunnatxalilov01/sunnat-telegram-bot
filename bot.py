import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"
CHANNELS = ["@test_uchun_kanall_1", "@test_uchun_kanall_2", "@test_uchun_kanall_3"]  # Kanal usernames

bot = telebot.TeleBot(TOKEN)
movies = {
    "15": "🎬 Kino: Avengers: Endgame",
    "22": "🎬 Kino: Titanic",
    "33": "🎬 Kino: Interstellar"
}

# Obuna tekshirish funksiyasi
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
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
    user_id = message.chat.id

    # **Obuna bo‘lganligini tekshiramiz**
    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        for channel in CHANNELS:
            markup.add(InlineKeyboardButton(f"🔗 Kanalga o'tish", url=f"https://t.me/{channel[1:]}"))
        markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(user_id, "❌ Avval quyidagi kanallarga obuna bo‘ling va tasdiqlang!", reply_markup=markup)
        return  # Kino yuborilmaydi

    # Kino kodini tekshirish
    movie_code = message.text.strip()
    response = movies.get(movie_code, "❌ Bunday kod topilmadi.")
    bot.send_message(user_id, response)

bot.polling(none_stop=True)
