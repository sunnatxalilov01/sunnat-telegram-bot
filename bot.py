# TOKEN = "7314638802:AAEGABdxn_p7CiqogkP0T8xcDKZL2pxWzbM"  # 🔹 Tokenni almashtiring
# TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # 🔹 Tokenni almashtiring
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # Bot tokenni shu yerga qo'ying
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"  # Kinolar saqlanadigan kanal
ADMIN_ID = 8936611  # Admin ID
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
    try:
        with open(SETTINGS_FILE, "w") as file:
            json.dump(settings, file, indent=4)
    except Exception as e:
        print(f"Sozlamalarni saqlashda xatolik: {e}")

def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_users(users):
    try:
        with open(USERS_FILE, "w") as file:
            json.dump(list(users), file, indent=4)
    except Exception as e:
        print(f"Foydalanuvchilarni saqlashda xatolik: {e}")

users = load_users()
settings = load_settings()

def check_subscription(user_id):
    channels = settings.get("channels", [])
    for channel in channels:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"Kanalga a'zolikni tekshirishda xatolik: {e}")
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
        markup.add(InlineKeyboardButton(f"🔗 {channel} kanaliga o'tish", url=f"https://t.me/{channel[1:]}"))
    markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))

    bot.send_message(user_id, "🔹 Iltimos, quyidagi kanallarga obuna bo‘ling va tasdiqlash tugmasini bosing:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    user_id = call.message.chat.id
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino ID raqamini kiriting:")
    else:
        bot.send_message(user_id, "❌ Siz hali barcha kanallarga obuna bo‘lmadingiz! Avval ularga qo‘shiling.")

@bot.message_handler(commands=['kanallar'])
def manage_channels(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")
        return

    bot.send_message(ADMIN_ID, "📌 Kanallarni sozlash: \n\n➕ Kanal qo‘shish: /add_channel @kanal_nomi\n➖ Kanal o‘chirish: /remove_channel @kanal_nomi\n📋 Kanallar ro‘yxati: /list_channels")

@bot.message_handler(commands=['add_channel'])
def add_channel(message):
    if message.chat.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(ADMIN_ID, "❌ Foydalanish: /add_channel @kanal_nomi")
        return

    channel = parts[1]
    if channel not in settings["channels"]:
        settings["channels"].append(channel)
        save_settings(settings)
        bot.send_message(ADMIN_ID, f"✅ {channel} qo‘shildi!")
    else:
        bot.send_message(ADMIN_ID, "⚠️ Bu kanal allaqachon mavjud!")

@bot.message_handler(commands=['remove_channel'])
def remove_channel(message):
    if message.chat.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(ADMIN_ID, "❌ Foydalanish: /remove_channel @kanal_nomi")
        return

    channel = parts[1]
    if channel in settings["channels"]:
        settings["channels"].remove(channel)
        save_settings(settings)
        bot.send_message(ADMIN_ID, f"✅ {channel} o‘chirildi!")
    else:
        bot.send_message(ADMIN_ID, "⚠️ Bunday kanal topilmadi!")

@bot.message_handler(commands=['list_channels'])
def list_channels(message):
    if message.chat.id != ADMIN_ID:
        return

    channels = settings.get("channels", [])
    if channels:
        bot.send_message(ADMIN_ID, "📋 Kanallar ro‘yxati:\n" + "\n".join(channels))
    else:
        bot.send_message(ADMIN_ID, "❌ Hozircha hech qanday kanal mavjud emas!")

@bot.message_handler(func=lambda message: message.text.isdigit())
def send_movie(message):
    user_id = message.chat.id
    if not check_subscription(user_id):
        send_subscription_message(user_id)
        return  

    message_id = int(message.text.strip())
    try:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 Do‘stlarga ulashish", switch_inline_query=str(message_id)))
        bot.copy_message(user_id, MOVIE_CHANNEL, message_id, reply_markup=markup)
    except Exception as e:
        print(f"Kino yuborishda xatolik: {e}")
        bot.send_message(user_id, "❌ Bunday Ko'd topilmadi yoki video mavjud emas!")

@bot.message_handler(commands=['reklama'])
def send_advertisement(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")
        return
    
    advertisement_text = "Bu yerda reklama matni bo'ladi."
    for user_id in users:
        try:
            bot.send_message(user_id, advertisement_text)
        except Exception as e:
            print(f"Xabar yuborilmadi: {user_id}, xatolik: {e}")
    
    bot.send_message(ADMIN_ID, "✅ Reklama barcha foydalanuvchilarga yuborildi!")

bot.polling(none_stop=True)
