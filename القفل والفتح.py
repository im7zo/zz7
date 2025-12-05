from telethon import events
from config import client
import re

# قاموس الإعدادات لكل دردشة
chat_locks = {}

def get_chat_lock(chat_id):
    if chat_id not in chat_locks:
        chat_locks[chat_id] = {
            "stickers": False,
            "photos": False,
            "videos": False,
            "voices": False,
            "gifs": False,
            "files": False,
            "links": False
        }
    return chat_locks[chat_id]


# ————————————————————————
# أوامر القفل
# ————————————————————————

@client.on(events.NewMessage(pattern=r"^\.قفل الملصقات$"))
async def lock_stickers(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["stickers"] = True
    await event.edit("• تم قفل الملصقات.\n• سيتم منع استلام الملصقات في هذه الدردشة فقط.")

@client.on(events.NewMessage(pattern=r"^\.قفل الصور$"))
async def lock_photos(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["photos"] = True
    await event.edit("• تم قفل الصور.\n• سيتم منع استلام الصور في هذه الدردشة فقط.")

@client.on(events.NewMessage(pattern=r"^\.قفل الفيديو$"))
async def lock_videos(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["videos"] = True
    await event.edit("• تم قفل الفيديو.\n• سيتم منع استلام الفيديوهات في هذه الدردشة فقط.")

@client.on(events.NewMessage(pattern=r"^\.قفل الصوت$"))
async def lock_voices(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["voices"] = True
    await event.edit("• تم قفل الأصوات.\n• سيتم منع استلام الأصوات في هذه الدردشة فقط.")

@client.on(events.NewMessage(pattern=r"^\.قفل GIF$"))
async def lock_gifs(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["gifs"] = True
    await event.edit("• تم قفل صور GIF.\n• سيتم منع استلام صور GIF في هذه الدردشة فقط.")

@client.on(events.NewMessage(pattern=r"^\.قفل الملفات$"))
async def lock_files(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["files"] = True
    await event.edit("• تم قفل الملفات.\n• سيتم منع استلام الملفات في هذه الدردشة فقط.")

@client.on(events.NewMessage(pattern=r"^\.قفل الروابط$"))
async def lock_links(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["links"] = True
    await event.edit("• تم قفل الروابط.\n• سيتم منع إرسال الروابط في هذه الدردشة فقط.")


# ————————————————————————
# أوامر الفتح
# ————————————————————————

@client.on(events.NewMessage(pattern=r"^\.فتح الملصقات$"))
async def unlock_stickers(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["stickers"] = False
    await event.edit("• تم فتح الملصقات.\n• سيتم السماح بالملصقات في هذه الدردشة.")

@client.on(events.NewMessage(pattern=r"^\.فتح الصور$"))
async def unlock_photos(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["photos"] = False
    await event.edit("• تم فتح الصور.\n• سيتم السماح بالصور في هذه الدردشة.")

@client.on(events.NewMessage(pattern=r"^\.فتح الفيديو$"))
async def unlock_videos(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["videos"] = False
    await event.edit("• تم فتح الفيديو.\n• سيتم السماح بالفيديوهات في هذه الدردشة.")

@client.on(events.NewMessage(pattern=r"^\.فتح الصوت$"))
async def unlock_voices(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["voices"] = False
    await event.edit("• تم فتح الأصوات.\n• سيتم السماح بالأصوات في هذه الدردشة.")

@client.on(events.NewMessage(pattern=r"^\.فتح GIF$"))
async def unlock_gifs(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["gifs"] = False
    await event.edit("• تم فتح صور GIF.\n• سيتم السماح بصور GIF في هذه الدردشة.")

@client.on(events.NewMessage(pattern=r"^\.فتح الملفات$"))
async def unlock_files(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["files"] = False
    await event.edit("• تم فتح الملفات.\n• سيتم السماح بالملفات في هذه الدردشة.")

@client.on(events.NewMessage(pattern=r"^\.فتح الروابط$"))
async def unlock_links(event):
    if not event.out: return
    get_chat_lock(event.chat_id)["links"] = False
    await event.edit("• تم فتح الروابط.\n• سيتم السماح بإرسال الروابط في هذه الدردشة.")


# ————————————————————————
# مراقبة الرسائل – الحذف حسب القفل
# ————————————————————————

@client.on(events.NewMessage(incoming=True))
async def block_media(event):

    if event.out:  
        return

    locks = get_chat_lock(event.chat_id)

    # ملصقات
    if locks["stickers"] and event.sticker:
        return await event.delete()

    # صور
    if locks["photos"] and event.photo:
        return await event.delete()

    # فيديو
    if locks["videos"] and event.video:
        return await event.delete()

    # أصوات
    if locks["voices"] and (event.voice or event.audio):
        return await event.delete()

    # GIF
    if locks["gifs"] and event.gif:
        return await event.delete()

    # ملفات
    if locks["files"] and event.document:
        # تجاهل الملفات التي هي أصلاً صوت/فيديو/صورة لأنها تتعالج فوق
        if not event.photo and not event.video and not event.gif:
            return await event.delete()

    # روابط (URL)
    if locks["links"]:
        if event.raw_text:
            if re.search(r"(https?://|t\.me/|www\.)", event.raw_text):
                return await event.delete()