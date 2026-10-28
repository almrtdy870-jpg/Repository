import asyncio
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

# 📌 التوكن الجديد والمعلومات الشخصية والجلسة
BOT_TOKEN = "9148106346:AAF6XnZ__06uK3SMUi0rZ19Ic5fbKyVw7r8"
ADMIN_ID = "@Hl6l6"
YrUsername = "@Hl6l6"

# الجلسة الجديدة التي تم توليدها وتحديثها خصيصاً لحسابك
SESSION_STRING = (
    "1AZWarzcBuxYPXQ4nabZHYHELXxrgrQubc1k56JYPx9fENrnj5bHRk2_9STHkYnK"
    "djLofuACyF3OHDSa3ff7WqJS049hEjGDqdp0c4amj_c7MHTiED_euNKDQ3uCDLPN"
    "9tXBrZ-v_ES7-MSdnlhaRazAfJ9PqQNuhGZLBLM1sK2K7YAlaM3X37E3LoDWoN-R"
    "0Kle23fYN92Enw4TiRMgi68k2aSB8lCwNNF2G6MNua1Ea2gPi9qPn9x3STalBIOQ"
    "NK-a7ft2viXILx2QUkcXX8vRk3Zvm1oT5CeymIKRhnEnJHim6aczzBy0exfocac0"
    "hGdlico0LjwKZZX7d9fg3zVPPL4IYQSE="
)

API_ID = 34558339
API_HASH = "8bfa63fc0de3d7c5ae8f7d3e6dab8751"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

is_hunting = False


@app.route("/")
def home():
  return "Username Hunter Bot is running successfully! ⚡"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


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
      c1 * 4,
      c1 * 5,
      f"{c1*3}{n1}{n2}",
      f"{n1}{c1*4}",
      f"{c1}{c2}{c1}{c2}",
      f"{c1}{c1}{c2}{c2}",
      f"{c1}{c2}{c2}{c1}",
      f"{c1}_{c2}{c1}{c2}",
      f"{c1}{c1}_{c1}{c1}",
      f"_{c1}{c1}{c1}_",
      f"{c1}_{c1}_{c1}",
      f"{c1}{c1}_{c1}",
      f"{c1}_{c1}{c1}",
      f"{sub_c1}{v1}{sub_c1}{v1}",
      f"{sub_c1}{sub_c1}{v1}{sub_c1}",
      f"{sub_c1}_{v1}{sub_c1}",
      f"{sub_c1}{v1}_{v1}{sub_c1}",
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
                  f"🎉 New UserName Caught!\n‹ UserName →"
                  f" @{username}\n‹ Claim → {claim} ›",
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


# أوامر التحكم بالبوت عبر تليجرام
@bot.message_handler(commands=["start_hunt", "ابدأ_الصيد"])
def start_hunting(message):
  global is_hunting
  is_hunting = True
  bot.reply_to(
      message,
      "🟢 تم تفعيل صيد اليوزرات التلقائي بنجاح!\nالبوت يبحث الآن في الخلفية.",
  )


@bot.message_handler(commands=["stop_hunt", "ايقاف_الصيد"])
def stop_hunting(message):
  global is_hunting
  is_hunting = False
  bot.reply_to(message, "🛑 تم إيقاف صيد اليوزرات المؤقت.")


@bot.message_handler(commands=["clean", "تنظيف_الملفات"])
def clear_files(message):
  try:
    open("banned4.txt", "w").close()
    open("fragment.txt", "w").close()
    open("flood.txt", "w").close()
    bot.reply_to(
        message,
        "🧹 تم تنظيف وتفريغ ملفات الفحص (Banned & Fragment) بنجاح!\nعادت"
        " الملفات فارغة وجاهزة.",
        parse_mode="Markdown",
    )
  except Exception as e:
    bot.reply_to(
        message, f"❌ حدث خطأ أثناء التنظيف: {e}", parse_mode="Markdown"
    )


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا مطورنا العزيز في بوت الصيد والحماية! 🛡️\nاستخدم الأمر"
      " /start_hunt لبدء الصيد.\nولتنظيف الملفات استخدم /clean.",
  )


def run_telegram_bot():
  try:
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(none_stop=True)
  except Exception as e:
    print(f"Polling error: {e}")


if __name__ == "__main__":
  # تشغيل سيرفر Flask في الخلفية لإبقاء الخدمة نشطة على Render
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  hunter_thread = threading.Thread(target=run_telethon_hunter, daemon=True)
  hunter_thread.start()

  bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
  bot_thread.start()
