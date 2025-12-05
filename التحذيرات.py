from telethon import TelegramClient, events, functions
from telethon.tl.types import ChatBannedRights
from config import client  # استيراد client من ملف محفوظ

# =======================
# إعدادات المطورين
# =======================
ALLOWED_USERS = [7902529889]  # آيدي الأشخاص المسموح لهم
MAX_WARNINGS = 3              # الحد الافتراضي للتحذيرات
warnings_db = {}              # تخزين التحذيرات: {chat_id: {user_id: عدد التحذيرات}}

# حقوق التقييد عند تجاوز التحذيرات
BAN_RIGHTS = ChatBannedRights(
    until_date=None,       # None = تقييد دائم
    send_messages=True,    # يمنع إرسال الرسائل
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    change_info=False,
    invite_users=False,
    pin_messages=False,
    view_messages=False    # يظل قادر على رؤية الرسائل
)

# =======================
# دالة التحقق من السماح
# =======================
def is_allowed(user_id):
    return user_id in ALLOWED_USERS

# =======================
# أمر إعطاء تحذير
# =======================
@client.on(events.NewMessage(pattern=r'^\.تحذير(?: |$)(.*)'))
async def warn_user(event):
    sender = event.sender_id
    if not is_allowed(sender):
        await event.edit(
            "- عذراً .. عزيزي\n"
            "- هذا الأمر خاص بمطور السورس"
        )
        return

    if not event.is_group:
        return

    chat_id = event.chat_id
    args = event.pattern_match.group(1).strip()

    # الشخص الذي يتم الرد عليه
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
    else:
        await event.edit("❗️يـجـب الـرد على رسـالة الشـخص المـراد تحـذيره")
        return

    reason = args if args else "بدون سبب"

    if chat_id not in warnings_db:
        warnings_db[chat_id] = {}
    if user_id not in warnings_db[chat_id]:
        warnings_db[chat_id][user_id] = 0

    warnings_db[chat_id][user_id] += 1
    count = warnings_db[chat_id][user_id]

    await event.edit(
        f"تـم تحـذير الشـخص عـدد التـحذيرات ، {count}/{MAX_WARNINGS}\n"
        f"السـبب: {reason}"
    )

    # إذا تجاوز الحد، يقيد الشخص
    if count >= MAX_WARNINGS:
        await client(functions.channels.EditBannedRequest(
            channel=chat_id,
            participant=user_id,
            banned_rights=BAN_RIGHTS
        ))
        await event.respond(
            f"تـم تقـييد الشـخص بـعد تجـاوز الـحد المـسموح مـن التـحذيـرات ({MAX_WARNINGS})"
        )

# =======================
# أمر تعديل الحد
# =======================
@client.on(events.NewMessage(pattern=r'^\.تعديل التحذيرات (\d+)'))
async def edit_max_warnings(event):
    sender = event.sender_id
    if not is_allowed(sender):
        await event.reply(
            "- عذراً .. عزيزي\n"
            "- هذا الأمر خاص بمطور السورس"
        )
        return

    global MAX_WARNINGS
    MAX_WARNINGS = int(event.pattern_match.group(1))
    await event.edit(f"تـم تـعديـل الـحد المـسموح للتـحذيـرات إلـى ، {MAX_WARNINGS}")

# =======================
# أمر حذف التحذيرات
# =======================
@client.on(events.NewMessage(pattern=r'^\.حذف التحذيرات'))
async def delete_warnings(event):
    sender = event.sender_id
    if not is_allowed(sender):
        await event.edit(
            "- عذراً .. عزيزي\n"
            "- هذا الأمر خاص بمطور السورس"
        )
        return

    if not event.is_group or not event.reply_to_msg_id:
        await event.edit("❗️يـجـب الـرد على رسـالة الشـخص المـراد حـذف تحـذيراته")
        return

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    chat_id = event.chat_id

    if chat_id in warnings_db and user_id in warnings_db[chat_id]:
        warnings_db[chat_id][user_id] = 0
        await event.edit("تـم حـذف جمـيع التـحذيـرات لهـذا الشـخص")
    else:
        await event.edit("لا تـوجـد تحـذيـرات لهـذا الشـخص")

# =======================
# أمر عرض التحذيرات
# =======================
@client.on(events.NewMessage(pattern=r'^\.التحذيرات'))
async def show_warnings(event):
    sender = event.sender_id
    if not is_allowed(sender):
        await event.edit(
            "- عذراً .. عزيزي\n"
            "- هذا الأمر خاص بمطور السورس"
        )
        return

    chat_id = event.chat_id
    if chat_id not in warnings_db or not warnings_db[chat_id]:
        await event.edit("لا تـوجـد تحـذيـرات حالـيًا فـي هـذه المجـموعـة")
        return

    text = "التـحذيـرات الحـالية\n"
    for user, count in warnings_db[chat_id].items():
        text += f"- [ID {user}]: {count} تحذيرات\n"

    await event.edit(text)

