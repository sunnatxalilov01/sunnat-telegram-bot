# TOKEN = "7314638802:AAEGABdxn_p7CiqogkP0T8xcDKZL2pxWzbM"  # 🔹 Tokenni almashtiring
# TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # 🔹 Tokenni almashtiring
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time  

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"
ADMIN_ID = 8936611
SETTINGS_FILE = "settings.json"
USERS_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"channels": []}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(list(users), file)

users = load_users()
settings = load_settings()

def check_subscription(user_id):
    channels = settings.get("channels", [])
    for channel in channels:
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
    if user_id not in users:
        users.add(user_id)
        save_users(users)
    
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino ID raqamini kiriting:")
    else:
        send_subscription_message(user_id)

def send_subscription_message(user_id):
    channels = settings.get("channels", [])
    if not channels:
        bot.send_message(user_id, "⚠️ Hozircha obuna bo‘lish uchun kanallar mavjud emas!")
        return
    
    markup = InlineKeyboardMarkup()
    for channel in channels:
        markup.add(InlineKeyboardButton("🔗 Kanalga o'tish", url=f"https://t.me/{channel[1:]}") )
    markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
    bot.send_message(user_id, "🔹 Iltimos, quyidagi kanallarga obuna bo‘ling va tasdiqlash tugmasini bosing:", reply_markup=markup)

@bot.message_handler(commands=['reklama'])
def reklama(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "📢 Reklama xabarini yuboring (matn, rasm yoki video).")
        bot.register_next_step_handler(message, send_advertisement)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

def send_advertisement(message):
    users = load_users()
    for user_id in users:
        try:
            if message.text:
                bot.send_message(user_id, message.text)
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=message.caption)
        except Exception:
            pass
    bot.send_message(ADMIN_ID, "✅ Reklama barcha foydalanuvchilarga yuborildi!")

bot.polling(none_stop=True)
