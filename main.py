import os
import sqlite3
import threading
import time
import telebot
from flask import Flask

# سحب التوكن من متغيرات البيئة في رندر
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

# إعداد قاعدة البيانات الداخلية SQLite لحفظ إعدادات المجموعات
conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء جدول إعدادات الحماية والقفل لكل مجموعة
cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_settings (
        chat_id INTEGER PRIMARY KEY,
        lock_links INTEGER DEFAULT 1,
        lock_usernames INTEGER DEFAULT 1,
        lock_photos INTEGER DEFAULT 0,
        lock_stickers INTEGER DEFAULT 0,
        lock_bots INTEGER DEFAULT 1
    )
""")
conn.commit()


@app.route("/")
def home():
  return "Merida/Omda Protection Bot is active and running 24/7!"


# دالة جلب إعدادات المجموعة أو إنشائها تلقائياً
def get_settings(chat_id):
  cursor.execute(
      "SELECT lock_links, lock_usernames, lock_photos, lock_stickers,"
      " lock_bots FROM group_settings WHERE chat_id = ?",
      (chat_id,),
  )
  row = cursor.fetchone()
  if not row:
    cursor.execute(
        "INSERT INTO group_settings (chat_id, lock_links, lock_usernames,"
        " lock_photos, lock_stickers, lock_bots) VALUES (?, 1, 1, 0, 0, 1)",
        (chat_id,),
    )
    conn.commit()
    return 1, 1, 0, 0, 1
  return row


# دالة التحقق من المشرفين
def is_admin(chat_id, user_id):
  try:
    member = bot.get_chat_member(chat_id, user_id)
    return member.status in ["creator", "administrator"]
  except:
    return False


# ترحيب بالأعضاء الجدد
@bot.message_handler(content_types=["new_chat_members"])
def welcome_new_member(message):
  for member in message.new_chat_members:
    name = member.first_name
    bot.reply_to(
        message,
        f"أهلاً بك يا <b>{name}</b> في المجموعة، نورتنا! 🌹\nيرجى الالتزام"
        " بالقوانين لعدم التعرض للتقييد.",
    )


# أمر البدء أو الـ /start
@bot.message_handler(commands=["start"])
def start_command(message):
  if message.chat.type == "private":
    bot.reply_to(
        message,
        "أهلاً بك في بوت الحماية المتكامل (نظام ميريدا والعمدة). 🛡️\nأضفني إلى"
        " مجموعتك وارفعني مشرفاً لأقوم بحمايتها بأعلى كفاءة!",
    )
  else:
    bot.reply_to(message, "بوت الحماية يعمل بكامل طاقته لحماية الجروب! ⚡")


# أمر الآيدي ومعلومات العضو والمجموعة (يدعم /id أو كلمة ايدي)
@bot.message_handler(
    func=lambda m: m.text
    and m.text.lower() in ["id", "الايدي", "ايدي", "/id", "/الايدي"]
)
def get_id(message):
  user = message.from_user
  chat = message.chat
  text = (
      f"<b>معلوماتك الشخصية:</b>\n"
      f"- الاسم: {user.first_name}\n"
      f"- الآيدي: <code>{user.id}</code>\n"
      f"- المعرف: @{user.username if user.username else 'لا يوجد'}\n\n"
      f"<b>معلومات المجموعة:</b>\n"
      f"- اسم المجموعة: {chat.title}\n"
      f"- آيدي الجروب: <code>{chat.id}</code>"
  )
  bot.reply_to(message, text)


# 🔒 أوامر القفل والفتح بالنص العادي (مثل بوتات العمدة وميريدا)
@bot.message_handler(
    func=lambda m: m.text
    and m.chat.type != "private"
    and m.text.lower()
    in [
        "قفل الروابط",
        "فتح الروابط",
        "قفل المعرفات",
        "فتح المعرفات",
        "قفل الصور",
        "فتح الصور",
        "قفل الملصقات",
        "فتح الملصقات",
        "قفل البوتات",
        "فتح البوتات",
    ]
)
def control_locks_text(message):
  if not is_admin(message.chat.id, message.from_user.id):
    bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
    return

  text = message.text.lower()
  chat_id = message.chat.id

  if text == "قفل الروابط":
    cursor.execute(
        "UPDATE group_settings SET lock_links = 1 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    bot.reply_to(message, "تم قفل الروابط بنجاح 🔒")
  elif text == "فتح الروابط":
    cursor.execute(
        "UPDATE group_settings SET lock_links = 0 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    bot.reply_to(message, "تم فتح الروابط بنجاح 🔓")

  elif text == "قفل المعرفات":
    cursor.execute(
        "UPDATE group_settings SET lock_usernames = 1 WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    bot.reply_to(message, "تم قفل المعرفات بنجاح 🔒")
  elif text == "فتح المعرفات":
    cursor.execute(
        "UPDATE group_settings SET lock_usernames = 0 WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    bot.reply_to(message, "تم فتح المعرفات بنجاح 🔓")

  elif text == "قفل الصور":
    cursor.execute(
        "UPDATE group_settings SET lock_photos = 1 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    bot.reply_to(message, "تم قفل الصور بنجاح 🔒")
  elif text == "فتح الصور":
    cursor.execute(
        "UPDATE group_settings SET lock_photos = 0 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    bot.reply_to(message, "تم فتح الصور بنجاح 🔓")

  elif text == "قفل الملصقات":
    cursor.execute(
        "UPDATE group_settings SET lock_stickers = 1 WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    bot.reply_to(message, "تم قفل الملصقات بنجاح 🔒")
  elif text == "فتح الملصقات":
    cursor.execute(
        "UPDATE group_settings SET lock_stickers = 0 WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    bot.reply_to(message, "تم فتح الملصقات بنجاح 🔓")


# 🚫 أوامر الإدارة الفورية (بالرد على الرسالة: حظر، كتم)
@bot.message_handler(commands=["ban", "حظر", "طرد"])
def ban_user(message):
  if message.chat.type == "private":
    return
  if not is_admin(message.chat.id, message.from_user.id):
    bot.reply_to(message, "هذا الأمر للمشرفين فقط! ❌")
    return

  if message.reply_to_message:
    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    try:
      bot.ban_chat_member(message.chat.id, target_id)
      bot.reply_to(message, f"تم حظر العضو <b>{target_name}</b> بنجاح! 🔨")
    except Exception as e:
      bot.reply_to(message, f"فشل الحظر. تأكد من صلاحيات البوت. الخطأ: {e}")
  else:
    bot.reply_to(message, "يرجى الرد على رسالة الشخص المراد حظره.")


@bot.message_handler(commands=["mute", "كتم"])
def mute_user(message):
  if message.chat.type == "private":
    return
  if not is_admin(message.chat.id, message.from_user.id):
    bot.reply_to(message, "هذا الأمر للمشرفين فقط! ❌")
    return

  if message.reply_to_message:
    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    try:
      bot.restrict_chat_member(message.chat.id, target_id, can_send_messages=False)
      bot.reply_to(message, f"تم كتم العضو <b>{target_name}</b> بنجاح! 🔇")
    except Exception as e:
      bot.reply_to(message, f"فشل الكتم. الخطأ: {e}")
  else:
    bot.reply_to(message, "يرجى الرد على رسالة الشخص المراد كتمه.")


# 🛡️ نظام الحماية التلقائي الشامل (النصوص، الصور، الملصقات)
@bot.message_handler(
    content_types=["text", "photo", "sticker", "document", "video"]
)
def comprehensive_protection(message):
  if message.chat.type == "private":
    return

  # استثناء المشرفين
  if is_admin(message.chat.id, message.from_user.id):
    return

  chat_id = message.chat.id
  lock_links, lock_usernames, lock_photos, lock_stickers, lock_bots = (
      get_settings(chat_id)
  )

  # فحص الرسائل النصية (الروابط والمعرفات)
  if message.content_type == "text" and message.text:
    text = message.text.lower()
    is_link = (
        "http://" in text
        or "https://" in text
        or "t.me/" in text
        or "www." in text
    )
    is_username = "@" in text

    if (lock_links and is_link) or (lock_usernames and is_username):
      try:
        bot.delete_message(chat_id, message.message_id)
        user_name = message.from_user.first_name
        warn = bot.send_message(
            chat_id,
            f"عذراً <b>{user_name}</b>، ممنوع نشر الروابط والمعرفات هنا! 🚫",
        )

        def delete_warn():
          time.sleep(4)
          try:
            bot.delete_message(chat_id, warn.message_id)
          except:
            pass

        threading.Thread(target=delete_warn).start()
        return
      except:
        pass

  # فحص الصور
  if message.content_type == "photo" and lock_photos:
    try:
      bot.delete_message(chat_id, message.message_id)
      return
    except:
      pass

  # فحص الملصقات
  if message.content_type == "sticker" and lock_stickers:
    try:
      bot.delete_message(chat_id, message.message_id)
      return
    except:
      pass


if __name__ == "__main__":

  def run_bot():
    print("Bot polling started successfully...")
    bot.infinity_polling(skip_pending=True)

  threading.Thread(target=run_bot).start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
