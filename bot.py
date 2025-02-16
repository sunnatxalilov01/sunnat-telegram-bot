import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time  

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # 🔹 Tokenni o'zingiznikiga almashtiring
CHANNELS = ["@test_uchun_kanall_1", "@test_uchun_kanall_2", "@test_uchun_kanall_3"]  # 🔹 Obuna bo‘lishi shart bo‘lgan kanallar
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"  # 🔹 Kinolar saqlanadigan kanal

bot = telebot.TeleBot(TOKEN)

movies = {
    "15": 2,  # 🔹 Avengers: Endgame (message_id)
    "22": 5,  # 🔹 Titanic (message_id)
    "33": 789   # 🔹 Interstellar (message_id)
}

def check_subscription(user_id):
    time.sleep(1)
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

    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        for channel in CHANNELS:
            markup.add(InlineKeyboardButton(f"🔗 Kanalga o'tish", url=f"https://t.me/{channel[1:]}"))
        markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(user_id, "❌ Avval quyidagi kanallarga obuna bo‘ling va tasdiqlang!", reply_markup=markup)
        return  

    movie_code = message.text.strip()
    message_id = movies.get(movie_code)

    if message_id:
        bot.copy_message(user_id, MOVIE_CHANNEL, message_id)  # ✅ Endi kino to‘g‘ri kanaldan olinadi
    else:
        bot.send_message(user_id, "❌ Bunday kod topilmadi.")

bot.polling(none_stop=True)
