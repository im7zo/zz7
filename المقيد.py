import re
import os
from telethon import events
from config import client

# مجلد التحميل
DOWNLOAD_FOLDER = "mahdi_z"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# دالة لتحديث الرسالة أثناء التحميل/الرفع
async def update_status(message, text):
    try:
        await message.edit(text)
    except:
        pass

# استخراج القناة + رقم الرسالة من الرابط
def parse_link(link: str):
    if "t.me/c/" in link:
        m = re.search(r"t\.me/c/(\d+)/(\d+)", link)
        return int("-100" + m.group(1)), int(m.group(2))
    else:
        m = re.search(r"t\.me/([^/]+)/(\d+)", link)
        return m.group(1), int(m.group(2))


@client.on(events.NewMessage(pattern=r"\.مقيد (.+)"))
async def save_restricted(event):
    link = event.pattern_match.group(1)

    try:
        chat, msg_id = parse_link(link)
    except:
        await event.reply("❌ رابط غير صالح")
        return

    try:
        msg = await client.get_messages(chat, ids=msg_id)
    except Exception as e:
        await event.reply(f"❌ فشل جلب الرسالة\n{e}")
        return

    if not msg:
        await event.reply("❌ الرسالة غير موجودة")
        return

    # 📝 نص فقط
    if msg.text and not msg.media:
        await event.reply(msg.text, formatting_entities=msg.entities)
        return

    # إرسال رسالة حالة للتحميل
    status_msg = await event.reply("⏳ انتظر... جاري التحميل")

    # 📸 ألبوم
    if msg.grouped_id:
        album = []
        async for m in client.iter_messages(
            chat,
            min_id=msg.id - 50,
            max_id=msg.id + 50
        ):
            if m.grouped_id == msg.grouped_id:
                album.append(m)

        album = sorted(album, key=lambda x: x.id)

        files = []
        text = None
        entities = None

        for m in album:
            file = await m.download_media(file=DOWNLOAD_FOLDER)
            files.append(file)
            if m.text and not text:
                text = m.text
                entities = m.entities
            await update_status(status_msg, f"⏳ جاري تحميل {len(files)}/{len(album)} ملفات...")

        await client.send_file(
            event.chat_id,
            files,
            caption=text,
            formatting_entities=entities
        )

        # حذف الملفات بعد الإرسال
        for f in files:
            if f and os.path.exists(f):
                os.remove(f)
        await status_msg.delete()
        return

    # 🎥 ميديا واحدة
    file = await msg.download_media(file=DOWNLOAD_FOLDER)
    await update_status(status_msg, "⏳ جاري رفع الملف...")
    await client.send_file(
        event.chat_id,
        file,
        caption=msg.text,
        formatting_entities=msg.entities
    )
    if file and os.path.exists(file):
        os.remove(file)
    await status_msg.delete()