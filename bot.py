import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time  

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # 🔹 Tokenni almashtiring
CHANNELS = ["@test_uchun_kanall_1", "@test_uchun_kanall_2", "@test_uchun_kanall_3"]  # 🔹 Obuna bo‘lishi shart bo‘lgan kanallar
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"  # 🔹 Kinolar saqlanadigan kanal
ADMIN_ID = 8936611  # 🔹 Admin ID

bot = telebot.TeleBot(TOKEN)

movies = {
    "15": 2,  # 🔹 Avengers: Endgame (message_id)
    "22": 5,  # 🔹 Titanic (message_id)
    "33": 8   # 🔹 Interstellar (message_id)
}

USER_FILE = "users.json"

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(list(users), file)

users = load_users()

def check_subscription(user_id):
    time.sleep(1)
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users.add(user_id)  # 🔹 Foydalanuvchini ro‘yxatga olish
    save_users(users)
    
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino kodini kiriting:")
    else:
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

@bot.message_handler(commands=['reklama'])
def reklama(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "📢 Reklama xabarini yuboring (matn, rasm yoki video).")
        bot.register_next_step_handler(message, send_advertisement)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

def send_advertisement(message):
    if message.text:  # 🔹 Matnli reklama
        for user_id in users:
            try:
                bot.send_message(user_id, message.text)
            except Exception:
                pass
    elif message.photo:  # 🔹 Rasmli reklama
        for user_id in users:
            try:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            except Exception:
                pass
    elif message.video:  # 🔹 Videoli reklama
        for user_id in users:
            try:
                bot.send_video(user_id, message.video.file_id, caption=message.caption)
            except Exception:
                pass
    else:
        bot.send_message(ADMIN_ID, "❌ Reklama noto‘g‘ri formatda!")

    bot.send_message(ADMIN_ID, "✅ Reklama barcha foydalanuvchilarga yuborildi!")

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
    
    if movie_code in movies:
        message_id = movies[movie_code]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 Do‘stlarga ulashish", switch_inline_query=movie_code))
        bot.copy_message(user_id, MOVIE_CHANNEL, message_id, reply_markup=markup)
    else:
        bot.send_message(user_id, "❌ Bunday kod topilmadi.")

bot.polling(none_stop=True)
