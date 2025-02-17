import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time  
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDK bilan ulanish
cred = credentials.Certificate('service_account_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

TOKEN = "7314638802:AAEGABdxn_p7CiqogkP0T8xcDKZL2pxWzbM"  # 🔹 Tokenni almashtiring
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

# Foydalanuvchilarni saqlash Firebase'ga
def save_user_to_firebase(user_id):
    user_ref = db.collection('users').document(str(user_id))
    user_ref.set({
        'user_id': user_id,
        'joined_at': firestore.SERVER_TIMESTAMP
    })

# ✅ Obuna tekshirish funksiyasi (TO‘G‘RILANGAN)
def check_subscription(user_id):
    time.sleep(1)  # API limitdan oshib ketmaslik uchun
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                continue  # Agar foydalanuvchi a’zo bo‘lsa, keyingi kanalga o‘tamiz
            else:
                return False  # Agar birorta kanalga a’zo bo‘lmasa, noto‘g‘ri qaytaramiz
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
            return False  # Agar kanal topilmasa yoki boshqa xatolik bo‘lsa, noto‘g‘ri deb qaytaramiz
    return True  # Agar hamma kanallarga a’zo bo‘lsa, to‘g‘ri qaytaramiz

# 🔹 Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users.add(user_id)
    save_users(users)
    save_user_to_firebase(user_id)  # Firebase'ga foydalanuvchini qo‘shish
    
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino ID raqamini kiriting:")
    else:
        send_subscription_message(user_id)

# 🔹 Obunani tekshirish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    user_id = call.message.chat.id
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Siz barcha kanallarga azo bo‘lgansiz! Endi kino ID raqamini kiriting:")
    else:
        bot.send_message(user_id, "❌ Siz hali barcha kanallarga obuna bo‘lmadingiz! Avval ularga qo‘shiling.")

# 🔹 Kanal obuna xabari (TO‘G‘RILANGAN)
def send_subscription_message(user_id):
    markup = InlineKeyboardMarkup()
    
    # Kanallar uchun tugmalar yaratish
    for channel in CHANNELS:
        markup.add(InlineKeyboardButton(f"🔗 {channel}", url=f"https://t.me/{channel[1:]}"))
    
    # Tasdiqlash tugmasi
    markup.add(InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subs"))

    bot.send_message(user_id, "🔹 Iltimos, quyidagi kanallarga obuna bo‘ling va **✅ Obunani tekshirish** tugmasini bosing.", reply_markup=markup)

# 🔹 Kino kodini qabul qilish
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

# 🔹 Botni doimiy ishlatish
bot.remove_webhook()
bot.infinity_polling()
