from asyncio import new_event_loop, set_event_loop
import os
from os import name, path
import random
from random import choice
import string
import threading
import time
from bs4 import BeautifulSoup as S
from flask import Flask
import requests
import telebot
from telethon import TelegramClient, errors, functions
from telethon.sessions import StringSession
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    DeleteChannelRequest,
    UpdateUsernameRequest,
)

# 📌 معلوماتك الشخصية والجلسة والتوكن
BOT_TOKEN = "8816325428:AAG5zvr8tq7-QuDOtaWEw8lM4PQMb_AFoJk"
ADMIN_ID = "@Hl6l6"
YrUsername = "@Hl6l6"
SESSION_STRING = "1BJWap1wBu5ga9zTpmb2mhZ1wl4b0hsZepwc_dZYMJ5wzfRGFWoRkq8cuEH265JJtc8ZqJSBqRVjMODEg6JUE65G_PLrGqGUC-atZAipwzeFZ63KCeSZEAQ9j6SDtIAIonvymzwuoeXNiObDTweFWXt7WqnLjPooru9-NI5-7CnmZ1cP6E_-AUlTmcykkCLCsfJHs6lnPKMltYgApu4mBNoPbO6dXxlK0Ixq3Z3u41GumSzi6TgBvA73BJ1mg0rGyh7LK_caPe1Ylx13f26DZ6j2DIJEXSz5vPaLdByYj-AsU3bteERwq_20CavGykotHnugJCyjY6uGQQoL1uVTZiRoif6VbBXQ="

API_ID = 25324581
API_HASH = "08feee5eeb6fc0f31d5f2d23bb2c31d0"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

is_hunting = False

# قائمة الكلمات والكلايش الممنوعة لحماية المجموعات
BANNED_WORDS = [
    # يمكنك إضافة الكلمات الإباحية أو الكلايش المخالفة هنا
    "كلمة_ممنوعة_1",
    "كلمة_ممنوعة_2",
]


@app.route("/")
def home():
  return "Combined Hunter & Protection Bot is running successfully! ⚡"


# دالة توليد الأنماط المتقدمة والمكررة الفخمة
def usernames():
  chars = string.ascii_lowercase
  digits = string.digits

  c1 = choice(chars)
  c2 = choice(chars)
  c3 = choice(chars)
  n1 = choice(digits)
  n2 = choice(digits)

  vowels = ["a", "e", "i", "o", "u"]
  consonants = [c for c in chars if c not in vowels]

  sub_c1 = choice(consonants)
  v1 = choice(vowels)

  random_patterns = [
      c1 * 4,  # aaaa
      c1 * 5,  # aaaaa
      f"{c1*3}{n1}{n2}",  # aaa12
      f"{n1}{c1*4}",  # 1aaaa
      f"{c1}{c2}{c1}{c2}",  # abab
      f"{c1}{c1}{c2}{c2}",  # aabb
      f"{c1}{c2}{c2}{c1}",  # abba
      f"{c1}_{c2}{c1}{c2}",  # a_bab
      f"{c1}{c1}_{c1}{c1}",  # aa_aa
      f"_{c1}{c1}{c1}_",  # _aaa_
      f"{c1}_{c1}_{c1}",  # a_a_a
      f"{c1}{c1}_{c1}",  # aa_a
      f"{c1}_{c1}{c1}",  # a_aa
      f"{sub_c1}{v1}{sub_c1}{v1}",  # cava
      f"{sub_c1}{sub_c1}{v1}{sub_c1}",  # ccac
      f"{sub_c1}_{v1}{sub_c1}",  # c_vc
      f"{sub_c1}{v1}_{v1}{sub_c1}",  # cv_vc
      f"{c1}{c2}{c1}{c2}{c1}",
      f"{c1}{c2}{c1}{c2}{c3}",
      f"{c1}_{c1}_{c2}",
      f"{c1}_{c2}_{c1}",
      f"{c1*3}{c2*2}",
      f"{c1*3}{c2}{c3}",
      f"{c1*2}{c2*2}{c3*2}",
      f"{c1*4}{c2}",
      f"{c1*2}{c2}{c1*2}",
      f"{c1*3}{n1*2}",
      f"{c1*3}{c2}{n1}",
  ]
  return choice(random_patterns)


# دالة فحص Fragment
def fragment_check(username):
  try:
    response = requests.get(
        f"https://fragment.com/username/{str(username)}", timeout=5
    ).text
    soup = S(response, "html.parser")
    ok = soup.find("meta", property="og:description").get("content")
    if (
        "An auction to get the Telegram" in ok
        or "Telegram and secure your ownership" in ok
        or "Check the current availability of" in ok
        or "Secure your name with blockchain" in ok
    ):
      return True
    elif "is taken" in ok:
      return "is taken"
    else:
      return False
  except:
    return "error"


# دالة الصيد الخلفية باستخدام Telethon
def run_telethon_hunter():
  global is_hunting
  loop = new_event_loop()
  set_event_loop(loop)

  async def hunter_main():
    global is_hunting
    if not path.exists("banned4.txt"):
      open("banned4.txt", "w").close()
    if not path.exists("fragment.txt"):
      open("fragment.txt", "w").close()
    if not path.exists("flood.txt"):
      open("flood.txt", "w").close()

    try:
      client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
      await client.start()
    except Exception as e:
      print(f"Telethon connection error: {e}")
      return

    while True:
      if is_hunting:
        username = usernames()
        file1 = open("banned4.txt", "r").read() or ""
        file2 = open("fragment.txt", "r").read() or ""
        if username in file1 or username in file2:
          continue

        try:
          ok = fragment_check(username)
        except:
          continue

        if not ok:
          try:
            check = await client(CheckUsernameRequest(username=username))
            if check:
              result = await client(
                  CreateChannelRequest(
                      title=f"{username}", about="", megagroup=False
                  )
              )
              try:
                await client(
                    UpdateUsernameRequest(
                        channel=result.chats[0], username=username
                    )
                )
                await client.send_message(
                    username,
                    f"‹  •~• : @IFIF13  ›\n‹ UserName → @{username} ›",
                )
                claim = True
              except Exception as e:
                await client.send_message(
                    YrUsername, f"⌯ Error Message .\nMessage : {e} ."
                )
                claim = False

              bot.send_message(
                  ADMIN_ID,
                  f"🎉 **New UserName Caught!**\n‹ UserName →"
                  f" `@{username}`\n‹ Claim → {claim} ›",
                  parse_mode="Markdown",
              )

              async for chat in client.iter_dialogs():
                if chat.name == f"[ {username} ]" and not chat.entity.username:
                  await client(DeleteChannelRequest(channel=chat.entity))
                  break
          except errors.rpcbaseerrors.BadRequestError:
            with open("banned4.txt", "a") as f:
              f.write(username + "\n")
          except errors.FloodWaitError as timer:
            time.sleep(timer.seconds)
          except:
            pass
        elif ok == "is taken":
          pass
        else:
          with open("fragment.txt", "a") as f:
            f.write(username + "\n")

        time.sleep(2)
      else:
        time.sleep(1)

  loop.run_until_complete(hunter_main())


# --- نظام حماية المجموعات (يحذف المخالفات والملصقات والكلايش حتى للمشرفين) ---
@bot.message_handler(
    content_types=[
        "text",
        "sticker",
        "photo",
        "video",
        "document",
        "animation",
    ]
)
def group_protection(message):
  # تجاهل المحادثات الخاصة (الخاص) وتطبيق الحماية على المجموعات فقط
  if message.chat.type not in ["supergroup", "group"]:
    return

  try:
    bot_id = bot.get_me().id
    if message.from_user.id == bot_id:
      return
  except:
    pass

  chat_id = message.chat.id
  message_id = message.id
  user = message.from_user

  should_delete = False
  violation_reason = ""

  # 1. منع الملصقات (يمكنك تفعيل حذف كل الملصقات أو ملصقات محددة)
  if message.content_type == "sticker":
    # إذا أردت منع جميع الملصقات في المجموعة اجعلها True، أو خصصها
    # should_Delete = True
    # violation_reason = "ملصق"
    pass

  # 2. فحص النصوص والكلايش والكلمات الممنوعة
  text_content = message.text or message.caption
  if text_content:
    text_lower = text_content.lower()
    for word in BANNED_WORDS:
      if word in text_lower:
        should_delete = True
        violation_reason = "محتوى نصي أو كليشة مخالفة"
        break

  # 3. فحص الصور والفيديوهات التي تحتوي على كابشن مخالف
  if message.content_type in ["photo", "video"] and message.caption:
    caption_lower = message.caption.lower()
    for word in BANNED_WORDS:
      if word in caption_lower:
        should_delete = True
        violation_reason = "صورة/فيديو بكابشن مخالف"
        break

  # التنفيذ الفوري للحذف (يحذف حتى لو المرسل مشرف)
  if should_delete:
    try:
      bot.delete_message(chat_id, message_id)
      bot.send_message(
          chat_id,
          f"⚠️ **تم حذف رسالة المخالف** (`{user.first_name}`)\n📌 **السبب:**"
          f" {violation_reason}",
          parse_mode="Markdown",
      )
    except Exception as e:
      print(f"Protection delete error: {e}")


# --- أوامر التحكم بالبوت ---
@bot.message_handler(commands=["start_hunt", "ابدأ_الصيد"])
def start_hunting(message):
  global is_hunting
  is_hunting = True
  bot.reply_to(
      message,
      "🟢 **تم تفعيل صيد اليوزرات التلقائي بنجاح!**\nالبوت يبحث الآن في الخلفية.",
  )


@bot.message_handler(commands=["stop_hunt", "ايقاف_الصيد"])
def stop_hunting(message):
  global is_hunting
  is_hunting = False
  bot.reply_to(message, "🛑 **تم إيقاف صيد اليوزرات المؤقت.**")


@bot.message_handler(commands=["clean", "تنظيف_الملفات"])
def clear_files(message):
  try:
    open("banned4.txt", "w").close()
    open("fragment.txt", "w").close()
    open("flood.txt", "w").close()
    bot.reply_to(
        message,
        "🧹 **تم تنظيف وتفريغ ملفات الفحص بنجاح!**",
        parse_mode="Markdown",
    )
  except Exception as e:
    bot.reply_to(
        message, f"❌ حدث خطأ أثناء التنظيف: `{e}`", parse_mode="Markdown"
    )


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا مطورنا العزيز! 🛡️\n- لبدء صيد اليوزرات: `/start_hunt`\n- لتنظيف"
      " الملفات: `/clean`\n- البوت يقوم أيضاً بحماية المجموعات تلقائياً.",
  )


def run_telegram_bot():
  try:
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(none_stop=True)
  except Exception as e:
    print(f"Polling error: {e}")


if __name__ == "__main__":
  # تشغيل صيد اليوزرات
  hunter_thread = threading.Thread(target=run_telethon_hunter, daemon=True)
  hunter_thread.start()

  # تشغيل بوت التليجرام (أوامر وحماية)
  bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
  bot_thread.start()

  # تشغيل سيرفر الويب
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
