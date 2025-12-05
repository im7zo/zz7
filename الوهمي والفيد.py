import asyncio
import re
from telethon import events
from config import client
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import DeleteHistoryRequest

# ضع هنا آيديك الشخصي
OWNER_ID = 7902529889  # <-- غيّر الرقم إلى آيديك

# ================= أوامر التخفي =================
@client.on(events.NewMessage(outgoing=True, pattern=r'\.كتابة(?: (\d+))?'))
async def typing_fake(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1) or 15)
    async with client.action(event.chat_id, 'typing'):
        await asyncio.sleep(seconds)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيد(?: (\d+))?'))
async def sending_video_fake(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1) or 15)
    async with client.action(event.chat_id, 'video'):
        await asyncio.sleep(seconds)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوتية(?: (\d+))?'))
async def sending_voice_fake(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1) or 15)
    async with client.action(event.chat_id, 'record-voice'):
        await asyncio.sleep(seconds)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.موقع(?: (\d+))?'))
async def sending_location_fake(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1) or 15)
    async with client.action(event.chat_id, 'location'):
        await asyncio.sleep(seconds)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ملف(?: (\d+))?'))
async def sending_file_fake(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1) or 15)
    async with client.action(event.chat_id, 'document'):
        await asyncio.sleep(seconds)

# ================= الردود التلقائية =================
import json
import os
from telethon import events
from config import client

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/replies.json"

# ---------------------------------------
# إنشاء الملفات تلقائيًا
# ---------------------------------------
def ensure_files():
    # إنشاء المجلد إذا لم يكن موجودًا
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # إنشاء ملف الردود إذا لم يكن موجودًا
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

# ---------------------------------------
# تحميل الردود من ملف json
# ---------------------------------------
def load_replies():
    ensure_files()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

# ---------------------------------------
# حفظ الردود إلى ملف json
# ---------------------------------------
def save_replies(data):
    ensure_files()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل الردود
auto_replies = load_replies()

# الكروبات اللي مفعّل بها الرد
enabled_replies = set()

# ==============[ التفعيل ]================
@client.on(events.NewMessage(outgoing=True, pattern=r"\.تفعيل هنا$"))
async def enable_group_replies(event):
    if event.is_group:
        enabled_replies.add(event.chat_id)
        await event.edit(" تـم تفـعيـل الـردود هنـا")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")

# ==============[ التعطيل ]================
@client.on(events.NewMessage(outgoing=True, pattern=r"\.تعطيل هنا$"))
async def disable_group_replies(event):
    if event.is_group:
        enabled_replies.discard(event.chat_id)
        await event.edit("تـم تـعطـيل الـردود هـنا")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")

# ==============[ إضافة رد ]================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضف رد \+ (.+) \+ (.+)$"))
async def add_auto_reply(event):
    if not event.is_group:
        return await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")

    chat_id = str(event.chat_id)
    question = event.pattern_match.group(1).lower().strip()
    answer = event.pattern_match.group(2).strip()

    if chat_id not in auto_replies:
        auto_replies[chat_id] = {}

    auto_replies[chat_id][question] = answer
    save_replies(auto_replies)

    await event.edit(f"تـم إضـافـة الـرد\n🔹 **{question}**\n🔸 → **{answer}**")

# ==============[ عرض الردود ]================
@client.on(events.NewMessage(outgoing=True, pattern=r"\.الردود$"))
async def show_replies(event):
    if not event.is_group:
        return await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")

    chat_id = str(event.chat_id)
    replies = auto_replies.get(chat_id, {})

    if not replies:
        return await event.edit("❗لا يـوجـد رد مـضـاف هـنا ")

    text = " **الـردود المـضافـة:**\n"
    for i, (q, a) in enumerate(replies.items(), 1):
        text += f"\n{i}- **{q}** → {a}"

    await event.edit(text)

# ==============[ حذف رد ]================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف رد \+ (.+)$"))
async def delete_reply(event):
    if not event.is_group:
        return await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")

    chat_id = str(event.chat_id)
    question = event.pattern_match.group(1).lower().strip()

    if chat_id in auto_replies and question in auto_replies[chat_id]:
        del auto_replies[chat_id][question]
        save_replies(auto_replies)
        return await event.edit(f"تـم حـذف الـرد: **{question}**")

    await event.edit("❗لـم يـتم العـثور علـى هـذا الـرد")

# ==============[ الرد التلقائي الحقيقي ]================
@client.on(events.NewMessage(incoming=True))
async def auto_reply_handler(event):
    if not event.is_group:
        return

    # لازم الرد مفعل في هذا الكروب
    if event.chat_id not in enabled_replies:
        return

    # تجاهل رسائلك أنت
    me = await client.get_me()
    if event.sender_id == me.id:
        return

    chat_id = str(event.chat_id)
    msg = event.raw_text.lower().strip()

    replies = auto_replies.get(chat_id, {})

    if msg in replies:
        await event.reply(replies[msg])

# ================= أمر تحميل الفيديو =================
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ف (.+)'))
async def yt_video(event):
    if event.sender_id != OWNER_ID:
        return  # فقط المالك يمكنه استخدام الأمر

    chat = event.chat_id
    query = event.pattern_match.group(1).strip()

    if query.startswith("."):
        query = query[1:]

    full_query = "فيد " + query
    status_msg = await event.edit("انتظر جاري البحث ...")

    try:
        async with client.conversation('@ssuu1bot') as conv:
            await conv.send_message(full_query)

            video_clip = None
            timeout = 30
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)

                    # الاشتراك في القناة إذا طلب البوت
                    if "عليك الأشتراك" in response.message:
                        try:
                            channel_name = re.search(r"قناة البوت : (@\w+)", response.message).group(1)
                            await client(JoinChannelRequest(channel_name))
                            await conv.send_message(full_query)
                            continue
                        except:
                            await status_msg.edit("لم أتمكن من الاشتراك في القناة المطلوبة.")
                            return

                    # التحقق من الفيديو
                    if response.video:
                        video_clip = response
                        break

                except asyncio.TimeoutError:
                    break

        if video_clip:
            await client.send_file(chat, file=video_clip.media, silent=True)
            await status_msg.delete()
        else:
            await status_msg.edit("المحتوى غير موجود أو لم يتم الرد في الوقت المحدد.")

    except Exception as e:
        await status_msg.edit(f"حدث خطأ أثناء التحميل: {e}")

    # حذف المحادثة مع البوت بعد الانتهاء
    try:
        await client(DeleteHistoryRequest(peer='@ssuu1bot', max_id=0, just_clear=False, revoke=True))
    except Exception as e:
        print(f"فشل حذف المحادثة: {e}")