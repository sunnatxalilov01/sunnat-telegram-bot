
# TOKEN = "7314638802:AAEGABdxn_p7CiqogkP0T8xcDKZL2pxWzbM"  # 🔹 Tokenni almashtiring
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import time  

# 🔹 Bot va GitHub sozlamalari
TOKEN = "7314638802:AAAGABdxn_p7CiqogkP0T8xcDKZL2pxWzbM"
CHANNELS = ["@test_uchun_kanall_1", "@test_uchun_kanall_2", "@test_uchun_kanall_3"]
MOVIE_CHANNEL = "@test_uchun_kanall_video_arxiv"
ADMIN_ID = 8936611  # 🔹 Admin ID

# 🔹 GitHub sozlamalari
GITHUB_TOKEN = "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"
REPO_OWNER = "sunnatxalilov01"
REPO_NAME = "sunnat-telegram-bot"
FILE_PATH = "users.json"
BRANCH = "main"

bot = telebot.TeleBot(TOKEN)

# 🔹 GitHub-dan users.json ni yuklash
def load_users():
    API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(API_URL, headers=HEADERS)
        if response.status_code == 200:
            file_data = response.json()
            content = file_data['content']
            sha = file_data['sha']
            users = json.loads(requests.utils.unquote(content).encode('utf-8'))
            return set(users), sha
        else:
            return set(), None
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return set(), None

# 🔹 users.json ni GitHub-ga saqlash
def save_users(users):
    API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    try:
        users_json = json.dumps(list(users), indent=2)
        users_encoded = requests.utils.quote(users_json)
        _, sha = load_users()

        data = {"message": "Update users.json", "content": users_encoded, "branch": BRANCH}
        if sha:
            data["sha"] = sha

        response = requests.put(API_URL, headers=HEADERS, json=data)
        if response.status_code in [200, 201]:
            print("✅ users.json GitHub-ga saqlandi!")
        else:
            print(f"❌ Xatolik: {response.json()}")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

users, _ = load_users()

# 🔹 Obuna tekshirish
def check_subscription(user_id):
    time.sleep(1)
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                continue
            else:
                return False
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
            return False
    return True

# 🔹 Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users.add(user_id)
    save_users(users)
    
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Kanallarga a’zo bo‘lgansiz! Kino ID kiriting:")
    else:
        send_subscription_message(user_id)

# 🔹 Obunani tekshirish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    user_id = call.message.chat.id
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ Kanallarga a’zo bo‘lgansiz! Kino ID kiriting:")
    else:
        bot.send_message(user_id, "❌ Kanallarga a’zo bo‘lmadingiz!")

# 🔹 Kanal obuna xabari
def send_subscription_message(user_id):
    markup = InlineKeyboardMarkup()
    for channel in CHANNELS:
        markup.add(InlineKeyboardButton(f"🔗 {channel}", url=f"https://t.me/{channel[1:]}"))
    markup.add(InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subs"))
    bot.send_message(user_id, "🔹 Kanallarga obuna bo‘ling va **✅ Obunani tekshirish** tugmasini bosing.", reply_markup=markup)

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

# 🔹 Botni ishga tushirish
bot.remove_webhook()
bot.infinity_polling()
