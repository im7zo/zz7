import os
import json
from telethon import events
from telethon.tl.types import DocumentAttributeAudio
from telethon.errors import MessageIdInvalidError
from telethon.tl.functions.channels import JoinChannelRequest
from config import client

DB_FILE = "memes.json"

# تحميل قاعدة البيانات
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        meme_db = json.load(f)
else:
    meme_db = {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(meme_db, f, indent=2)

def parse_telegram_link(link):
    parts = link.strip().split('/')
    try:
        msg_id = int(parts[-1])
        channel = parts[-2].replace('@', '')
        return channel, msg_id
    except:
        return None, None


# ────────────── إضافة ميم ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ميمز (https?://t.me/\S+) (.+)$'))
async def add_meme(event):
    link = event.pattern_match.group(1)
    key_raw = event.pattern_match.group(2).strip()  # بدون underscore

    channel_username, msg_id = parse_telegram_link(link)
    if not channel_username or not msg_id:
        return

    try:
        await client(JoinChannelRequest(channel_username))
    except Exception:
        pass

    try:
        message = await client.get_messages(channel_username, ids=msg_id)
    except:
        return

    has_voice = message.voice
    has_audio = message.document and any(
        isinstance(attr, DocumentAttributeAudio) for attr in message.document.attributes
    )

    if not (has_voice or has_audio):
        return

    # حفظ فقط الرابط + رقم الرسالة بدون أي حفظ للملف
    meme_db[key_raw.lower()] = {
        "channel": channel_username,
        "msg_id": msg_id
    }
    save_db()

    await event.edit(f"تـم حـفظ البصمـة **{key_raw}**.")


# ────────────── حذف ميم ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ازالة (.+)$'))
async def delete_meme(event):
    key = event.pattern_match.group(1).lower()
    if key not in meme_db:
        return

    del meme_db[key]
    save_db()
    await event.edit(f"تـم حـذف **{key}**.")


# ────────────── حذف كل البصمات ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ازالة البصمات$'))
async def clear_all_memes(event):
    meme_db.clear()
    save_db()
    await event.edit(" تـم حـذف جـميـع الميم المحـفوظـة")


# ────────────── عرض القائمة ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.قائمة الميمز$'))
async def list_memes(event):
    if not meme_db:
        return await event.edit("❗ لا تـوجـد ميم محـفوظـة")

    text = "قـائـمة المـيمـز \n\n"
    for key in meme_db:
        text += f"→ {key}\n"

    await event.edit(text)


# ────────────── تشغيل البصمة ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.(.+)$'))
async def play_meme(event):
    key = event.pattern_match.group(1).strip().lower()
    if key not in meme_db:
        return

    data = meme_db[key]
    channel = data["channel"]
    msg_id = data["msg_id"]

    try:
        message = await client.get_messages(channel, ids=msg_id)
    except:
        return

    if message:
        await client.send_file(event.chat_id, message.media, reply_to=event.reply_to_msg_id)
        await event.delete()