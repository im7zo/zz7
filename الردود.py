from telethon import events
from config import client
import pickle
import asyncio
import os
from datetime import datetime, timedelta

# -------- إعدادات --------
afk_mode = False
autores_disabled_chats = set()
last_reply_from_me = {}
last_message_from_user = {}

STOP_TIME = 5 * 60  # 5 دقائق
DEFAULT_REPLY = "تـم اسـتلام رسـالتـك، سـأرد عليـك قـريباً"

# -------- تشغيل/تعطيل الرد --------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تشغيل الرد$'))
async def تشغيل_الرد(event):
    global afk_mode
    afk_mode = True
    await event.edit("تـم تـشغـيل الـرد التلـقائي")
    await asyncio.sleep(2)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعطيل الرد$'))
async def تعطيل_الرد(event):
    global afk_mode
    afk_mode = False
    await event.edit("تـم تـعطـيل الـرد التلـقائي")
    await asyncio.sleep(2)
    await event.delete()

# -------- تعيين/حذف الكليشة --------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعيين كليشة الرد$'))
async def تعيين_كليشة(event):
    msg = await event.get_reply_message()
    if msg:
        with open('reply_template.pickle', 'wb') as f:
            pickle.dump(msg.text, f)
        await event.edit("تـم تـعيـين كـلـيـشـة الـرد")
    else:
        await event.edit("❗ قـم بـالـرد عـلى رسـالـة لتـعيينـها")
    await asyncio.sleep(2)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.حذف كليشة الرد$'))
async def حذف_الكليشة(event):
    if os.path.exists('reply_template.pickle'):
        os.remove('reply_template.pickle')
        await event.edit("تـم حـذف الكليشة، سـيـرجـع الـرد الافـتراضي")
    else:
        await event.edit("❗ لا يـوجـد كليشة ليتم حـذفها")
    await asyncio.sleep(2)
    await event.delete()

# -------- إيقاف/استئناف الرد بمحادثة --------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اوكف$'))
async def اوقف_الرد(event):
    autores_disabled_chats.add(event.chat_id)
    await event.edit("تـم إيـقـاف الـرد التلـقـائي فـي هـذه المـحادثة")
    await asyncio.sleep(2)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ارجع$'))
async def ارجع_الرد(event):
    chat_id = event.chat_id
    if chat_id in autores_disabled_chats:
        autores_disabled_chats.remove(chat_id)
        await event.edit("تـم اسـتئـنـاف الـرد التلـقـائي فـي هـذه المـحادثة")
    else:
        await event.edit("الـرد التلقـائي مـفـعـل أصـلاً هـنا")
    await asyncio.sleep(2)
    await event.delete()

# -------- تسجيل ردك على الشخص --------
@client.on(events.NewMessage(outgoing=True))
async def سجل_ردي(event):
    if event.is_private:
        last_reply_from_me[event.chat_id] = datetime.now()

# -------- تسجيل آخر رسالة من الشخص --------
@client.on(events.NewMessage(incoming=True))
async def سجل_رسالة_الشخص(event):
    if not event.is_private:
        return
    sender = await event.get_sender()
    if sender.bot:
        return
    last_message_from_user[event.chat_id] = datetime.now()

# -------- الرد التلقائي الذكي --------
@client.on(events.NewMessage(incoming=True))
async def الرد_التلقائي(event):
    global afk_mode

    if not afk_mode:
        return
    if not event.is_private or event.chat_id in autores_disabled_chats:
        return
    sender = await event.get_sender()
    if sender.bot:
        return

    now = datetime.now()
    chat_id = event.chat_id

    # توقف الرد بعد ردك
    if chat_id in last_reply_from_me:
        elapsed = (now - last_reply_from_me[chat_id]).total_seconds()
        if elapsed < STOP_TIME:
            return

    # توقف الرد مؤقت بعد آخر رسالة من الشخص
    if chat_id in last_message_from_user:
        elapsed_user = (now - last_message_from_user[chat_id]).total_seconds()
        if elapsed_user < STOP_TIME:
            return

    # تحميل الكليشة أو الكليشة الافتراضية
    if os.path.exists('reply_template.pickle'):
        with open('reply_template.pickle', 'rb') as f:
            reply_text = pickle.load(f)
    else:
        reply_text = DEFAULT_REPLY

    # تحميل الصورة إن وجدت
    if os.path.exists('reply_image.pickle'):
        with open('reply_image.pickle', 'rb') as f:
            image_path = pickle.load(f)
        if os.path.exists(image_path):
            try:
                await client.send_file(chat_id, image_path, caption=reply_text)
                return
            except:
                pass

    await event.reply(reply_text)