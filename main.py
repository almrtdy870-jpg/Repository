import asyncio
import os

# حل جذري ومضمون 100% لإجبار بايثون 3.14 على تشغيل حلقة الأحداث بدون أخطاء
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("خطأ: يرجى التأكد من تعيين متغيرات البيئة الثلاثة بشكل صحيح!")
    exit(1)

app = Client(
    "XPicCleanerBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply_text(
        "أهلاً بك عزيزي في بوت الحماية وإدارة المجموعات (XPic Cleaner).\n\n"
        "قم بإضافة البوت إلى مجموعتك واجعله مشرفاً ليقوم بحمايتها بكفاءة عالية!"
    )

@app.on_message(filters.command("الاوامر") & filters.private)
async def commands_list(client, message):
    text = (
        "📜 **قائمة الأوامر المتاحة:**\n\n"
        "• `/start` - بدء تشغيل البوت.\n"
        "• `/الاوامر` - عرض قائمة الأوامر."
    )
    await message.reply_text(text)

async def main():
    print("جاري تشغيل البوت الآن...")
    await app.start()
    print("تم تشغيل البوت بنجاح وأصبح متصلاً بتلغرام 24 ساعة! 🚀")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
