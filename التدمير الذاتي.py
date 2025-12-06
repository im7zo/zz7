from telethon import events
from config import client
import asyncio

# المتغير العام لوقت التدمير بالثواني
self_destruct_time = 0  # 0 يعني التعطيل

# أمر تفعيل التدمير الذاتي مع عدد الثواني
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تدمير ذاتي (\d+)$'))
async def set_self_destruct(event):
    global self_destruct_time
    seconds = int(event.pattern_match.group(1))
    if seconds <= 0:
        msg = await event.edit("لا يـمكن تعـيين وقـت أقـل مـن 1 ثـانية")
        await asyncio.sleep(3)
        await msg.delete()
        return

    self_destruct_time = seconds
    msg = await event.edit(f"تـم تفـعيل التدمير الذاتي،\nسيتم حذف كل رسالة ترسلها بعد {self_destruct_time} ثانية ✔️")
    await asyncio.sleep(3)
    await msg.delete()

# أمر تعطيل التدمير الذاتي
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تدمير تعطيل$'))
async def disable_self_destruct(event):
    global self_destruct_time
    self_destruct_time = 0
    msg = await event.edit("تـم تـعطيل التـدمير الـذاتي بنجـاح")
    await asyncio.sleep(3)
    await msg.delete()

# مراقبة الرسائل الصادرة في المجموعات لحذفها تلقائيًا
@client.on(events.NewMessage(outgoing=True))
async def auto_delete_messages(event):
    global self_destruct_time
    # حذف فقط في المجموعات
    if self_destruct_time > 0 and event.is_group:
        await asyncio.sleep(self_destruct_time)
        try:
            await event.delete()
        except:
            pass