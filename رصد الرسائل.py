from telethon import events, functions
from config import client
import asyncio
import json
import os

# =========================
# إعدادات التخزين
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

STORAGE_GROUP_FILE = os.path.join(DATA_FOLDER, "storage_group.json")
WATCHED_USERS_FILE = os.path.join(DATA_FOLDER, "watched_users.json")

STORAGE_GROUP_TITLE = "مجموعـة مراقبـة الرسائـل"
STORAGE_GROUP_BIO = "لا تقم بحذف هذه المجموعة أو التغيير إلى مجموعة عامـة (وظيفتهـا تخزيـن رسـائل الاشخاص المراقبين.)"

# =========================
# تحميل قائمة المراقبين من الملف
if os.path.exists(WATCHED_USERS_FILE):
    with open(WATCHED_USERS_FILE, "r") as f:
        watched_users = set(json.load(f))
else:
    watched_users = set()

# =========================
# دوال المساعدة
async def get_user_id(user_input):
    if user_input.startswith("@"):
        entity = await client.get_entity(user_input)
        return entity.id
    else:
        return int(user_input)

def save_watched_users():
    with open(WATCHED_USERS_FILE, "w") as f:
        json.dump(list(watched_users), f)

def save_group_id(group_id):
    with open(STORAGE_GROUP_FILE, "w") as f:
        json.dump({"group_id": group_id}, f)

def load_group_id():
    if os.path.exists(STORAGE_GROUP_FILE):
        with open(STORAGE_GROUP_FILE, "r") as f:
            data = json.load(f)
            return data.get("group_id")
    return None

async def get_or_create_storage_group():
    group_id = load_group_id()
    if group_id:
        try:
            entity = await client.get_entity(group_id)
            return entity
        except:
            pass

    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_group and dialog.name == STORAGE_GROUP_TITLE:
            save_group_id(dialog.id)
            return dialog.entity

    result = await client(functions.messages.CreateChatRequest(
        users=[],
        title=STORAGE_GROUP_TITLE
    ))
    group = result.chats[0]

    try:
        await client(functions.channels.EditAboutRequest(
            channel=group.id,
            about=STORAGE_GROUP_BIO
        ))
    except:
        pass

    save_group_id(group.id)
    return group

# ===========
# تفعيل الرصد
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.رصد الرسائل (.+)$'))
async def watch_user(event):
    user_input = event.pattern_match.group(1).strip()
    try:
        user_id = await get_user_id(user_input)
    except:
        msg = await event.edit("فـشل فـي الحـصول عـلى المـستخدم")
        await asyncio.sleep(3)
        return await msg.delete()

    watched_users.add(user_id)
    save_watched_users()
    await get_or_create_storage_group()

    msg = await event.edit(f"تـم تفـعيل رصـد الرسـائل للشـخص **{user_input}**")
    await asyncio.sleep(7)
    await msg.delete()

# ===========
# إلغاء الرصد
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.الغاء رصد الرسائل (.+)$'))
async def unwatch_user(event):
    user_input = event.pattern_match.group(1).strip()
    try:
        user_id = await get_user_id(user_input)
    except:
        msg = await event.edit("فـشل فـي الحـصول عـلى المـستخدم")
        await asyncio.sleep(7)
        return await msg.delete()

    if user_id in watched_users:
        watched_users.remove(user_id)
        save_watched_users()
        msg = await event.edit(f"تـم تعـطيل رصـد الرسـائل للشـخص **{user_input}**")
    else:
        msg = await event.edit("هـذا المـستخدم ليـس تحـت الرصـد")

    await asyncio.sleep(8)
    await msg.delete()

# ===========
# المراقبة الفعلية للرسائل
@client.on(events.NewMessage(incoming=True))
async def monitoring_handler(event):
    if event.sender_id in watched_users and event.is_group:
        storage_group = await get_or_create_storage_group()
        chat = await event.get_chat()
        sender = await event.get_sender()

        sender_link = f"@{sender.username}" if sender.username else f"[{sender.first_name}](tg://user?id={sender.id})"
        message_link = f"https://t.me/c/{event.chat.id}/{event.id}"

        text = (
            "تم التقاط رسالة من الشخص الذي تراقبة\n\n"
            f"⌔┊الكــروب : {chat.title}\n\n"
            f"⌔┊المـرسـل : {sender_link}\n\n"
        )

        # إذا كانت الرسالة ميديا (صورة، ملصق، gif، فيديو)
        if event.media:
            text += "⌔┊الرسـالـة : ميـديا\n\n"
        else:
            text += f"⌔┊الرسـالـة : {event.message.message}\n\n"

        text += f"⌔┊رابـط الرسـالة : [رابط]({message_link})"

        try:
            if event.media:
                await client.send_file(
                    storage_group.id,
                    event.media,
                    caption=text,
                    link_preview=False
                )
            else:
                await client.send_message(
                    storage_group.id,
                    text,
                    link_preview=False
                )
        except Exception as e:
            print("Error sending message:", e)