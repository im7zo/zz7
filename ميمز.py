import os
import json
from telethon import events
from telethon.tl.types import DocumentAttributeAudio
from telethon.errors import MessageIdInvalidError
from telethon.tl.functions.channels import JoinChannelRequest
from config import client

FOLDER = "memes"
os.makedirs(FOLDER, exist_ok=True)

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
    """تحويل رابط تيليجرام إلى (channel_username, message_id)"""
    try:
        parts = link.strip().split('/')
        msg_id = int(parts[-1])
        channel = parts[-2]
        if channel.startswith('@'):
            channel = channel[1:]
        return channel, msg_id
    except Exception:
        return None, None

# ────────────── إضافة ميم جديد ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ميمز (https?://t.me/\S+) (.+)$'))
async def add_meme(event):
    link = event.pattern_match.group(1)
    key_raw = event.pattern_match.group(2).lower().strip()
    key = key_raw.replace(" ", "_")

    channel_username, msg_id = parse_telegram_link(link)
    if not channel_username or not msg_id:
        return  # تجاهل بدون رد

    # الاشتراك بالقناة إذا خاصة
    try:
        await client(JoinChannelRequest(channel_username))
    except Exception:
        pass  # إذا لم نستطع الاشتراك، نحاول التحميل على أي حال

    try:
        message = await client.get_messages(channel_username, ids=msg_id)
    except MessageIdInvalidError:
        return
    except Exception:
        return

    # التحقق من وجود صوت أو بصمة
    if not message or (not message.voice and not (
        message.document and any(isinstance(attr, DocumentAttributeAudio) for attr in message.document.attributes)
    )):
        return

    # تحديد الامتداد الأصلي
    original_ext = "ogg"
    if message.file and getattr(message.file, 'name', None):
        original_ext = message.file.name.split('.')[-1]
    
    file_path = os.path.join(FOLDER, f"{key}.{original_ext}")
    await message.download_media(file=file_path)
    
    meme_db[key] = file_path
    save_db()

    await event.edit(f"تـم حـفظ المـيم **{key_raw}** بـنجـاح.")

# ────────────── حذف ميم معين ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ازالة (\S+)$'))
async def delete_meme(event):
    key = event.pattern_match.group(1).lower()
    if key not in meme_db:
        return  # تجاهل بدون رد

    try:
        os.remove(meme_db[key])
    except Exception:
        pass

    del meme_db[key]
    save_db()

    await event.edit(f"تـم حـذف الميـم **{key}**.")

# ────────────── حذف جميع الميمات ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ازالة_البصمات$'))
async def clear_all_memes(event):
    for file_path in meme_db.values():
        try:
            os.remove(file_path)
        except Exception:
            pass

    meme_db.clear()
    save_db()

    await event.edit(" تـم حـذف جـميـع الميم المحـفوظـة")

# ────────────── عرض قائمة الميمات ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.قائمة الميمز$'))
async def list_memes(event):
    if not meme_db:
        return await event.edit("❗ لا تـوجـد ميم محـفوظـة")

    text = "قـائـمة المـيمـز \n\n"
    for key in meme_db:
        text += f"→ {key}\n"

    await event.edit(text)

# ────────────── تشغيل الميم ──────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.(\S+)$'))
async def play_meme(event):
    key = event.pattern_match.group(1).strip().lower()
    if key in meme_db:
        await client.send_file(event.chat_id, meme_db[key], reply_to=event.reply_to_msg_id)
        await event.delete()