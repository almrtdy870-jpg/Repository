import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# قراءة متغيرات البيئة من Render
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("خطأ: يرجى التأكد من تعيين متغيرات البيئة الثلاثة بشكل صحيح!")
    exit(1)

# إعداد تطبيق البوت
app = Client(
    "XPicCleanerBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# إعداد قاعدة البيانات لحفظ الإعدادات
db = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        chat_id INTEGER PRIMARY KEY,
        clean_media INTEGER DEFAULT 0,
        anti_nuke INTEGER DEFAULT 1
    )
""")
db.commit()

# أمر البدء في الخاص
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("• المطور •", url="https://t.me/")]
    ])
    await message.reply_text(
        "أهلاً بك عزيزي في بوت الحماية وإدارة المجموعات (XPic Cleaner).\n\n"
        "قم بإضافة البوت إلى مجموعتك واجعله مشرفاً ليقوم بحمايتها وتطهيرها بكفاءة عالية!",
        reply_markup=keyboard
    )

# عرض الأوامر
@app.on_message(filters.command("الاوامر") & filters.private)
async def commands_list(client: Client, message: Message):
    text = (
        "📜 **قائمة الأوامر المتاحة:**\n\n"
        "• `/start` - بدء تشغيل البوت.\n"
        "• `/الاوامر` - عرض هذه القائمة.\n"
        "• أضف البوت إلى مجموعتك ليعمل تلقائياً في حماية المجموعة ومنع التفليش."
    )
    await message.reply_text(text)

# تشغيل البوت
print("جاري تشغيل البوت...")
app.run()
