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

# 📌 معلوماتك الشخصية والجلسة والتوكن الجديد
BOT_TOKEN = "8816325428:AAG5zvr8tq7-QuDOtaWEw8lM4PQMb_AFoJk"
ADMIN_ID = "@Hl6l6"
YrUsername = "@Hl6l6"
SESSION_STRING = "1BJWap1wBu5ga9zTpmb2mhZ1wl4b0hsZepwc_dZYMJ5wzfRGFWoRkq8cuEH265JJtc8ZqJSBqRVjMODEg6JUE65G_PLrGqGUC-atZAipwzeFZ63KCeSZEAQ9j6SDtIAIonvymzwuoeXNiObDTweFWXt7WqnLjPooru9-NI5-7CnmZ1cP6E_-AUlTmcykkCLCsfJHs6lnPKMltYgApu4mBNoPbO6dXxlK0Ixq3Z3u41GumSzi6TgBvA73BJ1mg0rGyh7LK_caPe1Ylx13f26DZ6j2DIJEXSz5vPaLdByYj-AsU3bteERwq_20CavGykotHnugJCyjY6uGQQoL1uVTZiRoif6VbBXQ="

API_ID = 25324581
API_HASH = "08feee5eeb6fc0f31d5f2d23bb2c31d0"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

is_hunting = False


@app.route("/")
def home():
  return "Username Hunter Bot is running successfully! ⚡"


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
      # 1. أنماط الحروف المتكررة كلياً أو جزئياً
      c1 * 4,  # aaaa
      c1 * 5,  # aaaaa
      f"{c1*3}{n1}{n2}",  # aaa12
      f"{n1}{c1*4}",  # 1aaaa
      # 2. أنماط التكرار المزدوج والمتناسق
      f"{c1}{c2}{c1}{c2}",  # abab
      f"{c1}{c1}{c2}{c2}",  # aabb
      f"{c1}{c2}{c2}{c1}",  # abba
      f"{c1}_{c2}{c1}{c2}",  # a_bab
      # 3. أنماط الشرطة السفلية المميزة والتكرار
      f"{c1}{c1}_{c1}{c1}",  # aa_aa
      f"_{c1}{c1}{c1}_",  # _aaa_
      f"{c1}_{c1}_{c1}",  # a_a_a
      f"{c1}{c1}_{c1}",  # aa_a
      f"{c1}_{c1}{c1}",  # a_aa
      # 4. النماذج شبيهة الكلمات والمنعكسة (صحيح + علة)
      f"{sub_c1}{v1}{sub_c1}{v1}",  # cava
      f"{sub_c1}{sub_c1}{v1}{sub_c1}",  # ccac
      f"{sub_c1}_{v1}{sub_c1}",  # c_vc
      f"{sub_c1}{v1}_{v1}{sub_c1}",  # cv_vc
      # 5. الأنماط الكلاسيكية السابقة
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
              # محاولة التثبيت (Claim)
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

              # إرسال تنبيه لك عبر البوت
              bot.send_message(
                  ADMIN_ID,
                  f"🎉 **New UserName Caught!**\n‹ UserName →"
                  f" `@{username}`\n‹ Claim → {claim} ›",
                  parse_mode="Markdown",
              )

              # تنظيف القنوات الوهمية
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


# أوامر التحكم بالبوت عبر تليجرام
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


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا مطورنا العزيز في بوت الصيد والحماية! 🛡️\nاستخدم الأمر"
      " `/start_hunt` لبدء الصيد.",
  )


def run_telegram_bot():
  try:
    bot.remove_webhook()  # لمنع تداخل الاتصالات وخطأ 409
    time.sleep(1)
    bot.infinity_polling(none_stop=True)
  except Exception as e:
    print(f"Polling error: {e}")


if __name__ == "__main__":
  # تشغيل صيد اليوزرات في الخلفية
  hunter_thread = threading.Thread(target=run_telethon_hunter, daemon=True)
  hunter_thread.start()

  # تشغيل البوت الأساسي
  bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
  bot_thread.start()

  # تشغيل سيرفر الويب على Render
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
