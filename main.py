import os
import threading
import telebot
from flask import Flask

# توكن البوت الخاص بك
TOKEN = '8760916906:AAHJCdwKarG5ujAm_K588y1adAG0pjRR80E'
bot = telebot.TeleBot(TOKEN)

# 1. إعداد خادم الويب البسيط (Flask) لكي تكتشف منصة Render أن التطبيق نشط
app = Flask(__name__)


@app.route('/')
def home():
  return 'Bot is running 24/7 successfully!'


# 2. أوامر بوت تيليجرام الخاصة بك
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(
      message, 'أهلاً بك! البوت يعمل الآن بشكل مستمر على مدار 24 ساعة 🚀'
  )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(message, 'تم استلام رسالتك: ' + message.text)


def run_bot():
  bot.infinity_polling()


if __name__ == '__main__':
  # تشغيل البوت في الخلفية
  threading.Thread(target=run_bot).start()

  # تشغيل خادم الويب على المنفذ المطلوب من Render
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)

