from config import client 
import os 
import json 
from telethon import events 
from telethon.tl.functions.contacts import BlockRequest 
from telethon.tl.functions.users import GetFullUserRequest 

# مسار حفظ الكليشة
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
PROTECT_FILE = os.path.join(DATA_FOLDER, "protect_msg.json")

# كليشة افتراضية
DEFAULT_PROTECTION_MESSAGE = (
    "━ 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 - الرد الآلــي 💪\n"
    "•─────────────────•\n\n"
    "❞ مرحبًـا  {name} ❝\n\n"
    "⤶ قد اكـون مشغـول أو غيـر موجـود حاليـًا ؟!\n"
    "⤶ ❨ هذه رسالتك رقم {remaining} مـن {max} المسموحة ⚠️❩\n"
    "⤶ لا تقـم بـ إزعاجـي وفي حال أزعجتني سـوف يتم حظـرك تلقائيًا . . .\n\n"
    "⤶ فقط قل سبب مجيئك وانتظـر الـرد ⏳"
)

# تحميل الكليشة من الملف أو إعادة الافتراضي
def load_protection_message():
    if os.path.exists(PROTECT_FILE):
        try:
            with open(PROTECT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("message", DEFAULT_PROTECTION_MESSAGE)
        except:
            pass
    return DEFAULT_PROTECTION_MESSAGE

# حفظ الكليشة في ملف
def save_protection_message(message):
    with open(PROTECT_FILE, "w", encoding="utf-8") as f:
        json.dump({"message": message}, f, ensure_ascii=False)

# حذف ملف الكليشة (استعادة الافتراضي)
def delete_protection_message_file():
    if os.path.exists(PROTECT_FILE):
        os.remove(PROTECT_FILE)

# المتغيرات العامة
PRIVATE_LOCK = False
ALLOWED_USERS = set()
USER_MESSAGE_COUNT = {}
BLOCKED_USERS = set()
MAX_MESSAGES = 7
PROTECTION_MESSAGE_TEMPLATE = load_protection_message()

# ======= الدوال للتحقق من الأوامر الصادرة مني =======
async def is_from_me(event):
    me = await client.get_me()
    return event.sender_id == me.id

# أوامر التحكم
@client.on(events.NewMessage(pattern=r"^\.تفعيل الحماية$"))
async def lock_private(event):
    if not await is_from_me(event): return
    global PRIVATE_LOCK
    PRIVATE_LOCK = True
    await event.edit("تـم تـفعيل نـظام الحـماية")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الحماية$"))
async def unlock_private(event):
    if not await is_from_me(event): return
    global PRIVATE_LOCK, USER_MESSAGE_COUNT, BLOCKED_USERS
    PRIVATE_LOCK = False
    USER_MESSAGE_COUNT.clear()
    BLOCKED_USERS.clear()
    await event.reply("تـم تعـطيل نـظام الحـماية")

@client.on(events.NewMessage(pattern=r"^\.تحديد الانذارات (\d+)$"))
async def set_max_warnings(event):
    if not await is_from_me(event): return
    global MAX_MESSAGES
    MAX_MESSAGES = int(event.pattern_match.group(1))
    await event.edit(f"تـم تعـيين عـدد الإنـذارات إلـى **{MAX_MESSAGES}**")

@client.on(events.NewMessage(pattern=r"^\.تعيين كليشة الحماية$"))
async def set_protection_message(event):
    if not await is_from_me(event): return
    global PROTECTION_MESSAGE_TEMPLATE
    if not event.is_reply:
        return await event.edit("❗️الرجاء الرد على رسالة تحتوي على الكليشة.")
    reply = await event.get_reply_message()
    if not reply.message:
        return await event.edit("❗️الرسالة المردود عليها لا تحتوي على نص.")
    PROTECTION_MESSAGE_TEMPLATE = reply.message
    save_protection_message(PROTECTION_MESSAGE_TEMPLATE)
    await event.edit("تـم تـحديث كليـشة الحـماية")

@client.on(events.NewMessage(pattern=r"^\.حذف كليشة الحماية$"))
async def delete_protection_message_cmd(event):
    if not await is_from_me(event): return
    global PROTECTION_MESSAGE_TEMPLATE
    delete_protection_message_file()
    PROTECTION_MESSAGE_TEMPLATE = DEFAULT_PROTECTION_MESSAGE
    await event.edit("تـم حـذف كليـشة الحـماية")

# ======= السماح / الرفض =======
@client.on(events.NewMessage(pattern=r"^\.سماح$"))
async def allow_user(event):
    if not await is_from_me(event): return
    if not event.is_reply:
        return await event.edit("❗️الرجاء الرد على رسالة الشخص المراد السماح له.")
    reply = await event.get_reply_message()
    user_id = reply.sender_id
    ALLOWED_USERS.add(user_id)
    USER_MESSAGE_COUNT.pop(user_id, None)
    await event.edit(f"تـم السـماح لـ [ {user_id} ] بـإرسـال الرسـائل بحـرية")

@client.on(events.NewMessage(pattern=r"^\.رفض$"))
async def disallow_user(event):
    if not await is_from_me(event): return
    if not event.is_reply:
        return await event.reply("❗️الرجاء الرد على رسالة الشخص المراد رفضه.")
    reply = await event.get_reply_message()
    user_id = reply.sender_id
    ALLOWED_USERS.discard(user_id)
    await event.edit(f"تـم رفـض المـستـخدم [ {user_id} ]")

# ======= نظام الحماية الأساسي =======
@client.on(events.NewMessage(incoming=True))
async def private_control(event):
    if not event.is_private:
        return
    sender = await event.get_sender()
    user_id = sender.id
    me = await client.get_me()
    if user_id == me.id or not PRIVATE_LOCK or user_id in ALLOWED_USERS:
        return
    USER_MESSAGE_COUNT[user_id] = USER_MESSAGE_COUNT.get(user_id, 0) + 1
    count = USER_MESSAGE_COUNT[user_id]
    if count > MAX_MESSAGES:
        await event.respond("🚫 لقد تجاوزت الحد المسموح من الرسائل.\n📵 تم حظرك تلقائيًا.")
        await client(BlockRequest(user_id))
        BLOCKED_USERS.add(user_id)
        return
    if PROTECTION_MESSAGE_TEMPLATE:
        await event.respond(PROTECTION_MESSAGE_TEMPLATE.format(
            name=sender.first_name or "صديقي",
            remaining=count,
            max=MAX_MESSAGES
        ))