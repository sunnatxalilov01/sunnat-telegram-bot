import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time  

TOKEN = "7817081851:AAG3ptyWEe1IpnImaeRZtw0mMQjmPi_nOXs"  # 🔹 Tokenni almashtiring
CHANNELS = ["@test_uchun_kanall_1", "@test_uchun_kanall_2", "@test_uchun_kanall_3"]  # 🔹 Obuna bo‘lishi shart bo‘lgan kanallar
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"  # 🔹 Kinolar saqlanadigan kanal
ADMIN_ID = 8936611  # 🔹 Admin ID
USER_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)

# Foydalanuvchilarni yuklash
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Foydalanuvchilarni saqlash
def save_users(users):
    try:
        with open(USER_FILE, "w") as file:
            json.dump(list(users), file, indent=2)
    except Exception as e:
        print(f"❌ Xatolik: {e}")

users = load_users()

# Obuna tekshirish
def check_subscription(user_id):
    time.sleep(1)
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['member', 'administrator', 'creator']:
                continue
            return False
        except Exception:
            return False
    return True

# Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users.add(user_id)
    save_users(users)
    
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino ID raqamini kiriting:")
    else:
        send_subscription_message(user_id)

# Obunani tekshirish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    user_id = call.message.chat.id
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino ID raqamini kiriting:")
    else:
        bot.send_message(user_id, "❌ Siz hali barcha kanallarga obuna bo‘lmadingiz! Avval ularga qo‘shiling.")

# Kanal obuna xabari
def send_subscription_message(user_id):
    markup = InlineKeyboardMarkup()
    for channel in CHANNELS:
        markup.add(InlineKeyboardButton(f"🔗 Kanalga o'tish", url=f"https://t.me/{channel[1:]}") )
    markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
    bot.send_message(user_id, "🔹 Iltimos, quyidagi kanallarga obuna bo‘ling va tasdiqlash tugmasini bosing:", reply_markup=markup)

# Admin uchun reklama yuborish
@bot.message_handler(commands=['reklama'])
def reklama(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "📢 Reklama xabarini yuboring (matn, rasm yoki video).")
        bot.register_next_step_handler(message, send_advertisement)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

# Reklama yuborish
def send_advertisement(message):
    global users
    users = load_users()
    success, failed = 0, 0
    
    for user_id in users:
        try:
            if message.text:
                bot.send_message(user_id, message.text)
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=message.caption)
            success += 1
        except Exception:
            failed += 1
    
    bot.send_message(ADMIN_ID, f"✅ Reklama {success} foydalanuvchiga yuborildi! ❌ {failed} foydalanuvchiga yuborilmadi.")

# Kino kodini qabul qilish
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
    except Exception:
        bot.send_message(user_id, "❌ Bunday Kod topilmadi yoki video mavjud emas!")

# Botni doimiy ishlatish
bot.remove_webhook()
bot.infinity_polling()
