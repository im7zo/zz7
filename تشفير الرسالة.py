from telethon import events
from config import client
import base64

# أمر التشفير
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تشفير$"))
async def encrypt_message(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return  # تجاهل أي شخص غير صاحب الحساب

    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.edit("❗️يـجـب الـرد على رسـالة تحـتوي نـص")
    try:
        original_text = reply.text
        encoded = base64.b64encode(original_text.encode("utf-8")).decode("utf-8")
        await event.edit(f"تـم التـشفـير \n`{encoded}`")
    except Exception as e:
        await event.edit(f"فـشـل التـشفـير \n{e}")


# أمر فك التشفير
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك التشفير$"))
async def decrypt_message(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return  # تجاهل أي شخص غير صاحب الحساب

    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.edit("❗️يـجـب الـرد على رسـالة مـشـفرة")
    try:
        text_to_decode = reply.text.strip("`")  # إزالة backticks إن وجدت
        decoded = base64.b64decode(text_to_decode.encode("utf-8")).decode("utf-8")
        await event.edit(f"تـم فـك التـشفـير\n{decoded}")
    except Exception as e:
        await event.edit(f" فـشـل فـك التـشفـير \n{e}")