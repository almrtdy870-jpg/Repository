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

# إعداد قاعدة البيانات SQLite لحفظ إعدادات المجموعات بشكل دائم
conn = sqlite3.connect("omda_bot.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء جدول الإعدادات للمجموعات
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_settings (
        chat_id INTEGER PRIMARY KEY,
        lock_links INTEGER DEFAULT 1,
        lock_usernames INTEGER DEFAULT 1
    )
""")
conn.commit()


@app.route("/")
def home():
  app_name = os.environ.get("RENDER_SERVICE_NAME", "Omda/Merida Protection Bot")
  return f"{app_name} is active and running 24/7!"


# دالة جلب إعدادات المجموعة أو إنشائها تلقائياً
def get_settings(chat_id):
  cursor.execute(
      "SELECT lock_links, lock_usernames FROM chat_settings WHERE chat_id = ?",
      (chat_id,),
  )
  row = cursor.fetchone()
  if not row:
    cursor.execute(
        "INSERT INTO chat_settings (chat_id, lock_links, lock_usernames) VALUES"
        " (?, 1, 1)",
        (chat_id,),
    )
    conn.commit()
    return 1, 1
  return row


# دالة للتحقق من أن المستخدم مشرف في المجموعة
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
        f"أهلاً بك يا <b>{name}</b> في المجموعه، نورتنا! 🌹\nيرجى الالتزام"
        " بالقوانين لعدم التعرض للحظر.",
    )


# أمر البدء
@bot.message_handler(commands=["start"])
def start_command(message):
  if message.chat.type == "private":
    bot.reply_to(
        message,
        "أهلاً بك عزيزي في بوت حماية المجموعات المتكامل (نظام العمدة وميريدا)."
        " 🛡️\nأضفني إلى مجموعتك واجعلني مشرفاً بصلاحيات كاملة!",
    )
  else:
    bot.reply_to(message, "بوت الحماية الشامل يعمل بكامل طاقته لحماية الجروب! ⚡")


# أمر الآيدي ومعلومات العضو والمجموعة
@bot.message_handler(commands=["id", "الايدي", "ايدي"])
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


# أوامر قفل وفتح الروابط والمعرفات
@bot.message_handler(
    commands=[
        "قفل_الروابط",
        "فتح_الروابط",
        "قفل_المعرفات",
        "فتح_المعرفات",
        "قفل الروابط",
        "فتح الروابط",
    ]
)
def group_control(message):
  if message.chat.type == "private":
    return
  if not is_admin(message.chat.id, message.from_user.id):
    bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
    return

  text = message.text
  chat_id = message.chat.id

  if "قفل" in text and "روابط" in text:
    cursor.execute(
        "UPDATE chat_settings SET lock_links = 1 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    bot.reply_to(message, "تم قفل الروابط بنجاح 🔒")
  elif "فتح" in text and "روابط" in text:
    cursor.execute(
        "UPDATE chat_settings SET lock_links = 0 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    bot.reply_to(message, "تم فتح الروابط بنجاح 🔓")
  elif "قفل" in text and "معرفات" in text:
    cursor.execute(
        "UPDATE chat_settings SET lock_usernames = 1 WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    bot.reply_to(message, "تم قفل المعرفات (الكليشات) بنجاح 🔒")
  elif "فتح" in text and "معرفات" in text:
    cursor.execute(
        "UPDATE chat_settings SET lock_usernames = 0 WHERE chat_id = ?",
        (chat_id,),
    )
    conn.commit()
    bot.reply_to(message, "تم فتح المعرفات بنجاح 🔓")


# 🚫 أوامر الإدارة (حظر وطرد)
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
      bot.reply_to(message, f"فشل الحظر، تأكد من صلاحيات البوت. الخطأ: {e}")
  else:
    bot.reply_to(message, "يرجى الرد على رسالة الشخص المراد حظره.")


# 🔇 أوامر الكتم
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


# 🛡️ نظام الحماية التلقائي (حذف الروابط والمعرفات بناءً على إعدادات المجموعة)
@bot.message_handler(func=lambda message: True, content_types=["text"])
def protection_system(message):
  if message.chat.type == "private":
    return

  # استثناء المشرفين
  if is_admin(message.chat.id, message.from_user.id):
    return

  lock_links, lock_usernames = get_settings(message.chat.id)
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
      bot.delete_message(message.chat.id, message.message_id)
      user_name = message.from_user.first_name
      warning = bot.send_message(
          message.chat.id,
          f"عذراً <b>{user_name}</b>، ممنوع نشر الروابط والمعرفات في هذه"
          " المجموعة! 🚫",
      )

      # حذف التحذير تلقائياً بعد 4 ثواني
      def delete_warning():
        time.sleep(4)
        try:
          bot.delete_message(message.chat.id, warning.message_id)
        except:
          pass

      threading.Thread(target=delete_warning).start()
    except:
      pass


if __name__ == "__main__":
  # تشغيل البوت بخلفية مستقلة
  def run_bot():
    print("Omda Ultimate Bot polling started...")
    bot.infinity_polling(skip_pending=True)

  threading.Thread(target=run_bot).start()

  # تشغيل سيرفر الويب لاستضافة رندر
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
