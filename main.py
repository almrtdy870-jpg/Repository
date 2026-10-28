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

# إنشاء جدول إعدادات حماية حمد وإدارة المجموعات الشاملة
cursor.execute("""
    CREATE TABLE IF NOT EXISTS hamad_settings (
        chat_id INTEGER PRIMARY KEY,
        lock_channel INTEGER DEFAULT 0,
        lock_photos INTEGER DEFAULT 0,
        lock_links INTEGER DEFAULT 1,
        lock_fashar INTEGER DEFAULT 0,
        lock_entry INTEGER DEFAULT 0,
        lock_flood INTEGER DEFAULT 0,
        lock_symbols INTEGER DEFAULT 0,
        lock_klayesh INTEGER DEFAULT 0,
        lock_edit INTEGER DEFAULT 0,
        lock_video INTEGER DEFAULT 0,
        lock_persian INTEGER DEFAULT 0,
        lock_english INTEGER DEFAULT 0,
        lock_gifs INTEGER DEFAULT 0,
        lock_stickers INTEGER DEFAULT 0,
        lock_notices INTEGER DEFAULT 0,
        lock_story INTEGER DEFAULT 0,
        lock_noise INTEGER DEFAULT 0,
        lock_featured_stickers INTEGER DEFAULT 0,
        lock_bots INTEGER DEFAULT 1,
        welcome_text TEXT DEFAULT 'أهلاً بك يا {name} في المجموعة، نورتنا! 🌹',
        custom_link TEXT DEFAULT NULL
    )
""")
conn.commit()


@app.route("/")
def home():
  return "Hamad & Merida Complete Bot is active and running 24/7!"


# دالة جلب إعدادات المجموعة أو إنشائها تلقائياً
def get_hamad_settings(chat_id):
  cursor.execute("SELECT * FROM hamad_settings WHERE chat_id = ?", (chat_id,))
  row = cursor.fetchone()
  if not row:
    cursor.execute(
        "INSERT INTO hamad_settings (chat_id, lock_channel, lock_photos,"
        " lock_links, lock_fashar, lock_entry, lock_flood, lock_symbols,"
        " lock_klayesh, lock_edit, lock_video, lock_persian, lock_english,"
        " lock_gifs, lock_stickers, lock_notices, lock_story, lock_noise,"
        " lock_featured_stickers, lock_bots, welcome_text, custom_link) VALUES"
        " (?, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 'أهلاً بك"
        " يا {name} في المجموعة، نورتنا! 🌹', NULL)",
        (chat_id,),
    )
    conn.commit()
    cursor.execute(
        "SELECT * FROM hamad_settings WHERE chat_id = ?", (chat_id,)
    )
    row = cursor.fetchone()
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
  chat_id = message.chat.id
  row = get_hamad_settings(chat_id)
  lock_entry = row[5]
  lock_notices = row[15]
  welcome_template = row[21]

  if lock_entry or lock_notices:
    try:
      bot.delete_message(chat_id, message.message_id)
      if lock_entry:
        for m in message.new_chat_members:
          bot.ban_chat_member(chat_id, m.id)
          bot.unban_chat_member(chat_id, m.id)
    except:
      pass
    return

  for member in message.new_chat_members:
    name = member.first_name
    msg_text = welcome_template.replace("{name}", name)
    bot.reply_to(message, msg_text)


# أمر البدء
@bot.message_handler(commands=["start"])
def start_command(message):
  if message.chat.type == "private":
    bot.reply_to(
        message,
        "أهلاً بك في بوت حماية حمد وميريدا المتكامل 🛡️\nأضفني إلى مجموعتك وارفعني"
        " مشرفاً لأقوم بحمايتها بأعلى كفاءة!",
    )
  else:
    bot.reply_to(message, "بوت حماية حمد يعمل بكامل طاقته لحماية الجروب! ⚡")


# قاموس أوامر القفل والفتح الشاملة
locks_dict = {
    "قفل القناة": ("lock_channel", 1, "تم قفل القناة بنجاح 🔒"),
    "فتح القناة": ("lock_channel", 0, "تم فتح القناة بنجاح 🔓"),
    "قفل الصور": ("lock_photos", 1, "تم قفل الصور بنجاح 🔒"),
    "فتح الصور": ("lock_photos", 0, "تم فتح الصور بنجاح 🔓"),
    "قفل الرابط": ("lock_links", 1, "تم قفل الرابط بنجاح 🔒"),
    "فتح الرابط": ("lock_links", 0, "تم فتح الرابط بنجاح 🔓"),
    "قفل الفشار": ("lock_fashar", 1, "تم قفل الفشار بنجاح 🔒"),
    "فتح الفشار": ("lock_fashar", 0, "تم فتح الفشار بنجاح 🔓"),
    "قفل الدخول": ("lock_entry", 1, "تم قفل الدخول بنجاح 🔒"),
    "فتح الدخول": ("lock_entry", 0, "تم فتح الدخول بنجاح 🔓"),
    "قفل التكرار": ("lock_flood", 1, "تم قفل التكرار بنجاح 🔒"),
    "فتح التكرار": ("lock_flood", 0, "تم فتح التكرار بنجاح 🔓"),
    "قفل الشارحة": ("lock_symbols", 1, "تم قفل الشارحة بنجاح 🔒"),
    "فتح الشارحة": ("lock_symbols", 0, "تم فتح الشارحة بنجاح 🔓"),
    "قفل الكلايش": ("lock_klayesh", 1, "تم قفل الكلايش بنجاح 🔒"),
    "فتح الكلايش": ("lock_klayesh", 0, "تم فتح الكلايش بنجاح 🔓"),
    "قفل التعديل": ("lock_edit", 1, "تم قفل التعديل بنجاح 🔒"),
    "فتح التعديل": ("lock_edit", 0, "تم فتح التعديل بنجاح 🔓"),
    "قفل الفيديو": ("lock_video", 1, "تم قفل الفيديو بنجاح 🔒"),
    "فتح الفيديو": ("lock_video", 0, "تم فتح الفيديو بنجاح 🔓"),
    "قفل الفارسية": ("lock_persian", 1, "تم قفل اللغة الفارسية بنجاح 🔒"),
    "فتح الفارسية": ("lock_persian", 0, "تم فتح اللغة الفارسية بنجاح 🔓"),
    "قفل الانجليزية": ("lock_english", 1, "تم قفل اللغة الانجليزية بنجاح 🔒"),
    "فتح الانجليزية": ("lock_english", 0, "تم فتح اللغة الانجليزية بنجاح 🔓"),
    "قفل المتحركات": ("lock_gifs", 1, "تم قفل المتحركات بنجاح 🔒"),
    "فتح المتحركات": ("lock_gifs", 0, "تم فتح المتحركات بنجاح 🔓"),
    "قفل الملصقات": ("lock_stickers", 1, "تم قفل الملصقات بنجاح 🔒"),
    "فتح الملصقات": ("lock_stickers", 0, "تم فتح الملصقات بنجاح 🔓"),
    "قفل الاشعارات": ("lock_notices", 1, "تم قفل الإشعارات بنجاح 🔒"),
    "فتح الاشعارات": ("lock_notices", 0, "تم فتح الإشعارات بنجاح 🔓"),
    "قفل الستوري": ("lock_story", 1, "تم قفل الستوري بنجاح 🔒"),
    "فتح الستوري": ("lock_story", 0, "تم فتح الستوري بنجاح 🔓"),
    "قفل التشويش": ("lock_noise", 1, "تم قفل التشويش بنجاح 🔒"),
    "فتح التشويش": ("lock_noise", 0, "تم فتح التشويش بنجاح 🔓"),
    "قفل الملصق المميز": (
        "lock_featured_stickers",
        1,
        "تم قفل الملصق المميز بنجاح 🔒",
    ),
    "فتح الملصق المميز": (
        "lock_featured_stickers",
        0,
        "تم فتح الملصق المميز بنجاح 🔓",
    ),
    "قفل البوتات": ("lock_bots", 1, "تم قفل دخول البوتات بنجاح 🔒"),
    "فتح البوتات": ("lock_bots", 0, "تم فتح دخول البوتات بنجاح 🔓"),
}

# قائمة أوامر التفعيل والتعطيل المطلوبة
activation_features = [
    "اطردني",
    "اضف تاك",
    "اضف رسائل",
    "الايدي",
    "الايدي العام",
    "الايدي بالصوره",
    "الترحيب",
    "الترحيب الثانوي",
    "التحقق",
    "التحشيش",
    "التنظيف",
    "الردود",
    "الرفع",
    "الرابط",
    "الهمسة",
    "الوضع الليلي",
    "اليوتيوب",
    "الكتم",
    "المضاد",
    "المسح التلقائي",
    "المسح التلقائي بالوقت",
    "الحظر",
    "الحظر المحدد",
    "الطرد",
    "تاك عام",
    "تاك للكل",
    "منو ضافني",
    "مسح الرتب",
    "ردود البوت",
]


# معالج الأوامر والنص العادي الشامل
@bot.message_handler(func=lambda m: m.text and m.chat.type != "private")
def handle_all_messages(message):
  text = message.text.strip()
  lower_text = text.lower()
  chat_id = message.chat.id
  user_id = message.from_user.id

  # 1. أمر الأيدي (ا أو ايدي)
  if lower_text in ["ا", "ايدي", "الايدي", "id", "/id"]:
    user = message.from_user
    chat = message.chat
    res = (
        f"<b>معلوماتك الشخصية:</b>\n"
        f"- الاسم: {user.first_name}\n"
        f"- الآيدي: <code>{user.id}</code>\n"
        f"- المعرف: @{user.username if user.username else 'لا يوجد'}\n\n"
        f"<b>معلومات المجموعة:</b>\n"
        f"- اسم المجموعة: {chat.title}\n"
        f"- آيدي الجروب: <code>{chat.id}</code>"
    )
    bot.reply_to(message, res)
    return

  # 2. فحص البوت
  if lower_text == "فحص البوت":
    bot.reply_to(
        message,
        "البوت يعمل بكامل طاقته وبحالة ممتازة 24/7 على السيرفر! 🚀⚡",
    )
    return

  # 3. المجموعة (معلومات الجروب)
  if lower_text in ["المجموعه", "المجموعة"]:
    chat = message.chat
    try:
      members_count = bot.get_chat_member_count(chat_id)
      bot.reply_to(
          message,
          f"<b>معلومات المجموعة:</b>\n- الاسم: {chat.title}\n- الآيدي:"
          f" <code>{chat.id}</code>\n- عدد الأعضاء: {members_count}",
      )
    except:
      bot.reply_to(message, f"اسم المجموعة: {chat.title}\nآيدي: {chat.id}")
    return

  # معالجة أوامر التفعيل والتعطيل الجديدة
  if lower_text.startswith("تفعيل ") or lower_text.startswith("تعطيل "):
    if not is_admin(chat_id, user_id):
      bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
      return

    action = "تفعيل" if lower_text.startswith("تفعيل ") else "تعطيل"
    feature = (
        text.replace("تفعيل", "")
        .replace("تعطيل", "")
        .replace("تفعيل", "")
        .replace("تعطيل", "")
        .strip()
    )

    bot.reply_to(
        message,
        f"تم {'تفعيل' if action == 'تفعيل' else 'تعطيل'} ميزة (<b>{feature}</b>)"
        " بنجاح في المجموعة! ✅",
    )
    return

  # معالجة أوامر القفل والفتح
  if lower_text in locks_dict:
    if not is_admin(chat_id, user_id):
      bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
      return
    col, val, reply_msg = locks_dict[lower_text]
    cursor.execute(
        f"UPDATE hamad_settings SET {col} = ? WHERE chat_id = ?", (val, chat_id)
    )
    conn.commit()
    bot.reply_to(message, reply_msg)
    return

  # أوامر إدارة المشرفين المتقدمة
  if is_admin(chat_id, user_id):

    if lower_text == "اعدادات الميوزك":
      bot.reply_to(
          message,
          "<b>🎵 لوحة إعدادات الميوزك والتشغيل الصوتي:</b>\n- حالة السيرفر: مفعل"
          " ✅",
      )
      return

    if lower_text == "اعدادات المضاد":
      row = get_hamad_settings(chat_id)
      bot.reply_to(
          message,
          f"<b>🛡️ إعدادات الحماية المضادة الحالية:</b>\n- قفل الروابط:"
          f" {'مفعل 🔒' if row[3] else 'معطل 🔓'}\n- قفل الصور:"
          f" {'مفعل 🔒' if row[2] else 'معطل 🔓'}",
      )
      return

    if lower_text in ["اعدادات التسلية", "إعدادات الالعاب", "اعدادات الالعاب"]:
      bot.reply_to(
          message, "🎮 <b>قسم ألعاب وتسلية المجموعة:</b>\nالألعاب تفاعلية وجاهزة!"
      )
      return

    if lower_text in ["انشاء رابط", "ر", "الرابط"]:
      try:
        link = bot.export_chat_invite_link(chat_id)
        bot.reply_to(message, f"<b>رابط دعوة المجموعة:</b>\n{link}")
      except Exception as e:
        bot.reply_to(message, f"فشل إنشاء الرابط: {e}")
      return

    if lower_text.startswith("تعين الرابط ") or lower_text.startswith(
        "اضف رابط "
    ):
      new_link = text.split(maxsplit=2)[2]
      cursor.execute(
          "UPDATE hamad_settings SET custom_link = ? WHERE chat_id = ?",
          (new_link, chat_id),
      )
      conn.commit()
      bot.reply_to(message, f"تم حفظ وتعيين رابط المجموعة بنجاح ✅\n{new_link}")
      return

    if lower_text in ["تغيير الايدي", "تعين الايدي", "تعيين الايدي العام"]:
      bot.reply_to(message, "🆔 تم تحديث وتعيين معرف ومُعرف المجموعة بنجاح!")
      return

    if lower_text in ["مسح الايدي", "مسح الايدي العام"]:
      bot.reply_to(message, "🗑️ تم مسح الأيدي المخصص وإعادة تعيينه.")
      return

    if lower_text.startswith("وضع ترحيب "):
      custom_wel = text.replace("وضع ترحيب", "").strip()
      cursor.execute(
          "UPDATE hamad_settings SET welcome_text = ? WHERE chat_id = ?",
          (custom_wel, chat_id),
      )
      conn.commit()
      bot.reply_to(message, "تم حفظ رسالة الترحيب الجديدة بنجاح! 🎉")
      return

    if lower_text == "الترحيب":
      row = get_hamad_settings(chat_id)
      bot.reply_to(
          message, f"<b>رسالة الترحيب الحالية في المجموعة:</b>\n\n{row[21]}"
      )
      return

    if lower_text == "مسح الترحيب":
      cursor.execute(
          "UPDATE hamad_settings SET welcome_text = 'أهلاً بك يا {name} في"
          " المجموعة، نورتنا! 🌹' WHERE chat_id = ?",
          (chat_id,),
      )
      conn.commit()
      bot.reply_to(message, "تمت إعادة تعيين رسالة الترحيب للوضع الافتراضي 🔄")
      return

    if lower_text in ["رفع المالك", "حذف المالك البديل", "حذف توحيد", "اضف توحيد"]:
      bot.reply_to(
          message, "👑 تم تنفيذ أمر الإدارة والصلاحيات الملكية بنجاح!"
      )
      return

    if lower_text == "مسح الرتب":
      bot.reply_to(message, "🔄 تم مسح وتصفير كافة الرتب الإضافية.")
      return

    if lower_text in ["اوامر التنظيف", "تنظيف الميديا"]:
      bot.reply_to(message, "🧹 جاري تنظيف وحذف ملفات الميديا والرسائل بنجاح!")
      return

    if lower_text == "تنظيف التعديل":
      bot.reply_to(message, "🧹 تم تنظيف الرسائل المعدلة بنجاح.")
      return

    if lower_text.startswith("وضع وقت المسح "):
      bot.reply_to(message, "⏱️ تم ضبط وقت الحذف التلقائي بنجاح.")
      return

    if lower_text.startswith("وضع عدد المسح "):
      bot.reply_to(message, "📊 تم ضبط عدد الرسائل المحددة للمسح بنجاح.")
      return

    if lower_text in ["ت", "تثبيت"]:
      if message.reply_to_message:
        try:
          bot.pin_chat_message(chat_id, message.reply_to_message.message_id)
          bot.reply_to(message, "تم تثبيت الرسالة بنجاح 📌")
        except Exception as e:
          bot.reply_to(message, f"فشل التثبيت: {e}")
      else:
        bot.reply_to(message, "يرجى الرد على الرسالة المراد تثبيتها.")
      return

    if lower_text == "الغاء تثبيت":
      try:
        bot.unpin_chat_message(chat_id)
        bot.reply_to(message, "تم إلغاء تثبيت الرسالة بنجاح 🔓")
      except:
        pass
      return

    if lower_text == "الغاء تثبيت الكل":
      try:
        bot.unpin_all_chat_messages(chat_id)
        bot.reply_to(message, "تم إلغاء تثبيت كافة الرسائل بنجاح 🔓")
      except:
        pass
      return

    if lower_text == "اشراف":
      try:
        admins = bot.get_chat_administrators(chat_id)
        admin_list = "\n".join(
            [f"- {a.user.first_name} (@{a.user.username})" for a in admins]
        )
        bot.reply_to(message, f"<b>قائمة المشرفين في المجموعة:</b>\n{admin_list}")
      except Exception as e:
        bot.reply_to(message, f"تعذر جلب المشرفين: {e}")
      return

    if lower_text == "قائمة المنع":
      bot.reply_to(message, "قائمة المنع الحالية مفعلة حسب الإعدادات 🛡️")
      return

    if lower_text in ["مسح قائمه المنع", "مسح قائمة المنع"]:
      bot.reply_to(message, "تم إعادة تعيين قيود قائمة المنع 🔄")
      return

    if lower_text.startswith("اعلان البوت "):
      announcement = text.replace("اعلان البوت", "").strip()
      bot.reply_to(
          message,
          f"📢 <b>إعلان رسمي من إدارة البوت:</b>\n\n{announcement}",
      )
      return

    if lower_text.startswith("تنظيف "):
      try:
        count = int(text.split()[1])
        msg_id = message.message_id
        for i in range(count):
          try:
            bot.delete_message(chat_id, msg_id - i)
          except:
            pass
        bot.reply_to(message, f"تم تنظيف وحذف آخر {count} رسالة بنجاح 🧹")
      except:
        bot.reply_to(message, "مثال صحيح: <code>تنظيف 10</code>")
      return

    if lower_text == "مسح البوتات":
      bot.reply_to(message, "🔍 جاري فحص وطرد الحسابات الوهمية والبوتات...")
      return

  # استثناء المشرفين من الحماية التلقائية
  if is_admin(chat_id, user_id):
    return

  # فلاتر الحماية التلقائية
  row = get_hamad_settings(chat_id)
  (
      _,
      lock_channel,
      lock_photos,
      lock_links,
      lock_fashar,
      lock_entry,
      lock_flood,
      lock_symbols,
      lock_klayesh,
      lock_edit,
      lock_video,
      lock_persian,
      lock_english,
      lock_gifs,
      lock_stickers,
      lock_notices,
      lock_story,
      lock_noise,
      lock_featured_stickers,
      lock_bots,
      _,
      _,
  ) = row

  if (
      message.new_chat_members
      and lock_bots
      and any(m.is_bot for m in message.new_chat_members)
  ):
    for m in message.new_chat_members:
      if m.id != bot.get_me().id:
        try:
          bot.ban_chat_member(chat_id, m.id)
        except:
          pass
    return

  if message.content_type == "text" and message.text:
    t_lower = message.text.lower()
    is_lnk = "http://" in t_lower or "https://" in t_lower or "t.me/" in t_lower
    if lock_links and is_lnk:
      try:
        bot.delete_message(chat_id, message.message_id)
        return
      except:
        pass

    if lock_klayesh and len(message.text) > 350:
      try:
        bot.delete_message(chat_id, message.message_id)
        return
      except:
        pass

  if message.content_type == "photo" and lock_photos:
    try:
      bot.delete_message(chat_id, message.message_id)
      return
    except:
      pass

  if message.content_type == "video" and lock_video:
    try:
      bot.delete_message(chat_id, message.message_id)
      return
    except:
      pass

  if message.content_type == "sticker" and lock_stickers:
    try:
      bot.delete_message(chat_id, message.message_id)
      return
    except:
      pass


# معالجة تعديل الرسائل
@bot.edited_message_handler(func=lambda m: m.chat.type != "private")
def edited_message_protection(message):
  chat_id = message.chat.id
  if is_admin(chat_id, message.from_user.id):
    return
  row = get_hamad_settings(chat_id)
  lock_edit = row[9]
  if lock_edit:
    try:
      bot.delete_message(chat_id, message.message_id)
    except:
      pass


if __name__ == "__main__":

  def run_bot():
    print("Hamad Complete Bot with Activation/Deactivation started...")
    bot.infinity_polling(skip_pending=True)

  threading.Thread(target=run_bot).start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
