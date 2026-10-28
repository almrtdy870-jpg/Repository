import os
import threading
import time
import telebot
from flask import Flask

# سحب التوكن من متغيرات البيئة في رندر
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

# تخزين مؤقت للتحكم بالسبام ومنع التكرار
user_last_message = {}
user_message_count = {}


@app.route("/")
def home():
    return "Omda Full Protection Bot is active and running!"


# دالة للتحقق من أن المستخدم مشرف أو منشئ
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
            f"أهلاً بك يا <b>{name}</b> في المجموعه، نورتنا! 🌹\nيرجى الالتزام بالقوانين لعدم التعرض للحظر.",
        )


# أمر البدء (Start)
@bot.message_handler(commands=["start"])
def start_command(message):
    if message.chat.type == "private":
        bot.reply_to(
            message,
            "أهلاً بك عزيزي في بوت حماية المجموعات المتكامل (طراز العمدة). 🛡️\nأضفني إلى مجموعتك واجعلني مشرفاً بأصلاحيات كاملة لأقوم بحمايتها!",
        )
    else:
        bot.reply_to(message, "بوت الحماية يعمل بكامل طاقتة وجاهز لخدمتكم! 🛡️")


# 🚫 أوامر الإدارة (حظر وكتم)
@bot.message_handler(commands=["ban", "طرد"])
def ban_user(message):
    if message.chat.type == "private":
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
        return
    
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        if is_admin(message.chat.id, target_id):
            bot.reply_to(message, "لا يمكنك حظر مشرف في المجموعة! ⚠️")
            return
        try:
            bot.ban_chat_member(message.chat.id, target_id)
            bot.reply_to(message, f"تم حظر العضو <b>{target_name}</b> بنجاح! 🔨")
        except Exception as e:
            bot.reply_to(message, f"فشل الحظر، تأكد من صلاحيات البوت. الخطأ: {e}")
    else:
        bot.reply_to(message, "يرجى الرد على رسالة الشخص المراد حظره واستخدام الأمر.")


@bot.message_handler(commands=["mute", "كتم"])
def mute_user(message):
    if message.chat.type == "private":
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
        return

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        if is_admin(message.chat.id, target_id):
            bot.reply_to(message, "لا يمكنك كتم مشرف في المجموعة! ⚠️")
            return
        try:
            # تقييد العضو (منعه من إرسال الرسائل)
            bot.restrict_chat_member(
                message.chat.id, 
                target_id, 
                can_send_messages=False
            )
            bot.reply_to(message, f"تم كتم العضو <b>{target_name}</b> بنجاح! 🔇")
        except Exception as e:
            bot.reply_to(message, f"فشل الكتم، تأكد من صلاحيات البوت. الخطأ: {e}")
    else:
        bot.reply_to(message, "يرجى الرد على رسالة الشخص المراد كتمه.")


@bot.message_handler(commands=["unmute", "فتح_الكتم"])
def unmute_user(message):
    if message.chat.type == "private":
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "عذراً، هذا الأمر للمشرفين فقط! ❌")
        return

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        try:
            # إعادة الصلاحيات للعضو
            bot.restrict_chat_member(
                message.chat.id,
                target_id,
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            bot.reply_to(message, f"تم رفع الكتم عن العضو <b>{target_name}</b> بنجاح! 🔊")
        except Exception as e:
            bot.reply_to(message, f"فشل رفع الكتم. الخطأ: {e}")
    else:
        bot.reply_to(message, "يرجى الرد على رسالة الشخص المراد فتح الكتم عنه.")


# 🛡️ نظام الحماية التلقائي (روابط، معرفات، سبام)
@bot.message_handler(func=lambda message: True, content_types=["text"])
def protection_filters(message):
    if message.chat.type == "private":
        return

    # استثناء المشرفين من الحذف أو الفحص
    if is_admin(message.chat.id, message.from_user.id):
        return

    text = message.text.lower()

    # 1. فحص الروابط ومعرفات تيليجرام
    if "http://" in text or "https://" in text or "t.me/" in text or "www." in text or "@" in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            user_name = message.from_user.first_name
            warning = bot.send_message(
                message.chat.id,
                f"عذراً <b>{user_name}</b>، ممنوع نشر الروابط والمعرفات هنا! 🚫 تم حذف رسالتك."
            )
            
            # حذف التحذير بعد 5 ثواني
            def delete_warning():
                time.sleep(5)
                try:
                    bot.delete_message(message.chat.id, warning.message_id)
                except:
                    pass
            threading.Thread(target=delete_warning).start()
            return
        except:
            pass


if __name__ == "__main__":
    # تشغيل البوت بخلفية مستقلة
    def run_bot():
        print("Omda Bot polling started successfully...")
        bot.infinity_polling(skip_pending=True)

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # تشغيل سيرفر الويب الخاص برندر
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
