import os
import time
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus

# ==================== إعدادات البوت (تلقائية من المنصة) ====================
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

app = Client("XPicCleanerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ==================== إعداد قاعدة البيانات الشاملة ====================
conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS group_settings (
    chat_id INTEGER PRIMARY KEY,
    del_photo INTEGER DEFAULT 1,
    del_video INTEGER DEFAULT 1,
    del_round_video INTEGER DEFAULT 1,
    del_animation INTEGER DEFAULT 1,
    del_sticker INTEGER DEFAULT 1,
    del_emoji INTEGER DEFAULT 1,
    del_forward INTEGER DEFAULT 1,
    del_story INTEGER DEFAULT 1,
    del_link INTEGER DEFAULT 1,
    detector_status INTEGER DEFAULT 1,
    detector_punishment TEXT DEFAULT 'restrict',
    delete_message INTEGER DEFAULT 1,
    alert_private INTEGER DEFAULT 1,
    alert_group INTEGER DEFAULT 1,
    mention_admins INTEGER DEFAULT 1,
    antinuke_enabled INTEGER DEFAULT 1,
    antinuke_limit INTEGER DEFAULT 2,
    antinuke_time INTEGER DEFAULT 900,
    clean_count INTEGER DEFAULT 50
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_actions (
    chat_id INTEGER,
    admin_id INTEGER,
    action_time REAL
)
""")
conn.commit()

def get_settings(chat_id):
    cursor.execute("SELECT * FROM group_settings WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO group_settings (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
        cursor.execute("SELECT * FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
    return row

def update_setting(chat_id, column, value):
    cursor.execute(f"UPDATE group_settings SET {column} = ? WHERE chat_id = ?", (value, chat_id))
    conn.commit()

# ==================== قائمة الأوامر الرئيسية والأزرار ====================
@app.on_message(filters.command(["الاوامر", "أوامر"], prefixes=["/", "،", "."]) & filters.group)
async def panel_command(client: Client, message: Message):
    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply("عذراً، هذا الأمر للمشرفين فقط 🛑")
    except:
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👮‍♂️ المساعدين", callback_data="sec_assistants"), InlineKeyboardButton("🆓 الاحرار", callback_data="sec_free")],
        [InlineKeyboardButton("🧹 المنظفين", callback_data="sec_cleaners"), InlineKeyboardButton("⚙️ إعدادات الكاشف", callback_data="sec_detector")],
        [InlineKeyboardButton("🛑 مانع التفليش", callback_data="sec_antinuke"), InlineKeyboardButton("🗑 قسم التنظيف", callback_data="sec_cleaner_menu")]
    ])
    
    await message.reply(
        "• **XPic Cleaner 🔥**\n\n"
        "**مرحباً بك في قائمة الأوامر الرئيسية ⚡️**\n"
        "اختر القسم الذي تريد التحكم به من الأسفل 👇",
        reply_markup=keyboard
    )

# ==================== معالجة الأزرار التفاعلية ====================
@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    settings = get_settings(chat_id)

    if data == "main_menu":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👮‍♂️ المساعدين", callback_data="sec_assistants"), InlineKeyboardButton("🆓 الاحرار", callback_data="sec_free")],
            [InlineKeyboardButton("🧹 المنظفين", callback_data="sec_cleaners"), InlineKeyboardButton("⚙️ إعدادات الكاشف", callback_data="sec_detector")],
            [InlineKeyboardButton("🛑 مانع التفليش", callback_data="sec_antinuke"), InlineKeyboardButton("🗑 قسم التنظيف", callback_data="sec_cleaner_menu")]
        ])
        await callback_query.message.edit_text("• **XPic Cleaner 🔥**\n\nمرحباً بك في قائمة الأوامر الرئيسية ⚡️", reply_markup=keyboard)

    elif data == "sec_cleaner_menu":
        p = "✅" if settings[1] else "❌"
        v = "✅" if settings[2] else "❌"
        rv = "✅" if settings[3] else "❌"
        anim = "✅" if settings[4] else "❌"
        stk = "✅" if settings[5] else "❌"
        emj = "✅" if settings[6] else "❌"
        fwd = "✅" if settings[7] else "❌"
        stry = "✅" if settings[8] else "❌"
        lnk = "✅" if settings[9] else "❌"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"فيديو دائري: {rv}", callback_data="toggle_rv"), InlineKeyboardButton(f"فيديو: {v}", callback_data="toggle_v"), InlineKeyboardButton(f"صور: {p}", callback_data="toggle_p")],
            [InlineKeyboardButton(f"إيموجي مميز: {emj}", callback_data="toggle_emj"), InlineKeyboardButton(f"GIF: {anim}", callback_data="toggle_anim"), InlineKeyboardButton(f"ملصقات: {stk}", callback_data="toggle_stk")],
            [InlineKeyboardButton(f"الروابط: {lnk}", callback_data="toggle_lnk"), InlineKeyboardButton(f"الستوري: {stry}", callback_data="toggle_stry"), InlineKeyboardButton(f"التوجيه: {fwd}", callback_data="toggle_fwd")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu")]
        ])
        await callback_query.message.edit_text("⚙️ **مرحباً بك في قسم التنظيم والتنظيف التلقائي:**", reply_markup=keyboard)

    elif data.startswith("toggle_"):
        col_map = {
            "toggle_p": "del_photo", "toggle_v": "del_video", "toggle_rv": "del_round_video",
            "toggle_anim": "del_animation", "toggle_stk": "del_sticker", "toggle_emj": "del_emoji",
            "toggle_fwd": "del_forward", "toggle_stry": "del_story", "toggle_lnk": "del_link"
        }
        col = col_map.get(data)
        if col:
            index_map = {"del_photo": 1, "del_video": 2, "del_round_video": 3, "del_animation": 4, "del_sticker": 5, "del_emoji": 6, "del_forward": 7, "del_story": 8, "del_link": 9}
            curr_val = settings[index_map[col]]
            new_val = 0 if curr_val == 1 else 1
            update_setting(chat_id, col, new_val)
            await callback_query.answer("تم التحديث بنجاح ✅")
            return await callback_handler(client, CallbackQuery(id=callback_query.id, from_user=callback_query.from_user, chat_instance=callback_query.chat_instance, message=callback_query.message, data="sec_cleaner_menu"))

    elif data == "sec_detector":
        det_st = "مفعل ✅" if settings[10] else "معطل ❌"
        pun = settings[11]
        pun_text = "تقييد ⚠️" if pun == "restrict" else ("حظر 🚫" if pun == "ban" else "بلا عقوبة 🟢")
        del_m = "نعم ✅" if settings[12] else "لا ❌"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"حالة الكاشف ⟵ {det_st}", callback_data="det_toggle")],
            [InlineKeyboardButton(f"العقوبة ⟵ {pun_text}", callback_data="det_punishment_menu")],
            [InlineKeyboardButton(f"حذف الرسالة ⟵ {del_m}", callback_data="det_del_toggle")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu")]
        ])
        await callback_query.message.edit_text("⚙️ **إعدادات الكاشف والتحكم الذكي:**", reply_markup=keyboard)

    elif data == "det_toggle":
        new_v = 0 if settings[10] == 1 else 1
        update_setting(chat_id, "detector_status", new_v)
        await callback_query.answer("تم تغيير حالة الكاشف ✅")
        return await callback_handler(client, CallbackQuery(id=callback_query.id, from_user=callback_query.from_user, chat_instance=callback_query.chat_instance, message=callback_query.message, data="sec_detector"))

    elif data == "det_del_toggle":
        new_v = 0 if settings[12] == 1 else 1
        update_setting(chat_id, "delete_message", new_v)
        await callback_query.answer("تم التحديث ✅")
        return await callback_handler(client, CallbackQuery(id=callback_query.id, from_user=callback_query.from_user, chat_instance=callback_query.chat_instance, message=callback_query.message, data="sec_detector"))

    elif data == "det_punishment_menu":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("تقييد ⚠️", callback_data="set_pun_restrict"), InlineKeyboardButton("حظر 🚫", callback_data="set_pun_ban"), InlineKeyboardButton("بلا عقوبة 🟢", callback_data="set_pun_none")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="sec_detector")]
        ])
        await callback_query.message.edit_text("⚠️ **اختر نوع العقوبة عند المخالفة:**", reply_markup=keyboard)

    elif data.startswith("set_pun_"):
        p_type = data.replace("set_pun_", "")
        update_setting(chat_id, "detector_punishment", p_type)
        await callback_query.answer("تم تحديث العقوبة بنجاح ✅")
        return await callback_handler(client, CallbackQuery(id=callback_query.id, from_user=callback_query.from_user, chat_instance=callback_query.chat_instance, message=callback_query.message, data="sec_detector"))

    elif data == "sec_antinuke":
        an_status = "✅ مفعل" if settings[16] else "❌ معطل"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"مانع التفليش: {an_status}", callback_data="toggle_antinuke")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu")]
        ])
        await callback_query.message.edit_text(
            f"🛡 **قسم مانع التفليش (Anti-Nuke)**\n\n"
            f"• الوضع الحالي: مسموح حظر {settings[17]} نفر خلال {int(settings[18]/60)} دقيقة.\n"
            f"• الإجراء التلقائي: تنزيل المشرف وسحب صلاحياته فوراً.",
            reply_markup=keyboard
        )

    elif data == "toggle_antinuke":
        new_v = 0 if settings[16] == 1 else 1
        update_setting(chat_id, "antinuke_enabled", new_v)
        await callback_query.answer("تم تحديث مانع التفليش ✅")
        return await callback_handler(client, CallbackQuery(id=callback_query.id, from_user=callback_query.from_user, chat_instance=callback_query.chat_instance, message=callback_query.message, data="sec_antinuke"))

    elif data in ["sec_assistants", "sec_free", "sec_cleaners"]:
        titles = {"sec_assistants": "المساعدين 👮‍♂️", "sec_free": "الأحرار 🆓", "sec_cleaners": "المنظفين 🧹"}
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu")]])
        await callback_query.message.edit_text(f"📌 **أوامر قسم ({titles.get(data)})**\n\nيمكنك التحكم بهذا القسم وإضافة الأعضاء بسهولة عبر الأوامر الخاصة.", reply_markup=keyboard)

    await callback_query.answer()

# ==================== نظام تنظيف الميديا التلقائي ====================
@app.on_message(filters.group & (filters.photo | filters.video | filters.animation | filters.sticker | filters.entity("url")))
async def media_cleaner_handler(client: Client, message: Message):
    if not message.from_user:
        return
    
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return
    except:
        pass

    chat_id = message.chat.id
    st = get_settings(chat_id)

    should_delete = False
    if message.photo and st[1] == 1:
        should_delete = True
    elif message.video and st[2] == 1:
        should_delete = True
    elif message.animation and st[4] == 1:
        should_delete = True
    elif message.sticker and st[5] == 1:
        should_delete = True
    elif message.link and st[9] == 1:
        should_delete = True
    elif message.forward_date and st[7] == 1:
        should_delete = True

    if should_delete:
        try:
            await message.delete()
        except Exception as e:
            print(f"فشل حذف الميديا: {e}")

# ==================== نظام مانع التفليش (Anti-Nuke) ====================
@app.on_chat_member_updated()
async def antinuke_system(client: Client, member_update):
    chat_id = member_update.chat.id
    st = get_settings(chat_id)
    
    if st[16] == 0:
        return

    if member_update.new_chat_member and member_update.new_chat_member.status == ChatMemberStatus.BANNED:
        current_time = time.time()
        admin_id = member_update.from_user.id if member_update.from_user else None
        
        if not admin_id:
            return

        try:
            chat = await client.get_chat(chat_id)
            if chat.owner and chat.owner.user.id == admin_id:
                return
        except:
            pass

        cursor.execute("DELETE FROM admin_actions WHERE chat_id = ? AND action_time < ?", (chat_id, current_time - st[18]))
        cursor.execute("INSERT INTO admin_actions VALUES (?, ?, ?)", (chat_id, admin_id, current_time))
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM admin_actions WHERE chat_id = ? AND admin_id = ?", (chat_id, admin_id))
        count = cursor.fetchone()[0]

        if count > st[17]:
            try:
                await client.promote_chat_member(
                    chat_id=chat_id,
                    user_id=admin_id,
                    is_anonymous=False,
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
                await client.send_message(
                    chat_id,
                    f"⚠️ **تحذير مانع التفليش (Anti-Nuke)**\n\n"
                    f"• قام أحد المشرفين بتجاوز الحد المسموح للإجراءات المتكررة!\n"
                    f"• الإجراء المتخذ: **تم تنزيل المشرف تلقائياً** لحماية المجموعة 🛡"
                )
            except Exception as e:
                print(f"فشل تنزيل المشرف: {e}")

print("Bot is running successfully on Render...")
app.run()
