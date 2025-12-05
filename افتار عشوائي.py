import random
from telethon import events
from config import client  # استيراد client من ملف config

AVATAR_CHANNEL = "zzio5"
MIN_MSG_ID = 462
MAX_MSG_ID = 564

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.عشوائي$"))
async def random_avatar(event):
    await event.delete()  # حذف الأمر من الدردشة
    await send_avatar(event.chat_id)

async def send_avatar(chat_id):
    try:
        msg_id = random.randint(MIN_MSG_ID, MAX_MSG_ID)
        msg = await client.get_messages(AVATAR_CHANNEL, ids=msg_id)

        if msg and msg.photo:
            caption = "⌯ اتمنى أن تنال إعجابك"
            await client.send_file(chat_id, msg.photo, caption=caption)
        else:
            await client.send_message(chat_id, "⌯ لم يتم العثور على صورة صالحة.")
    except Exception as e:
        await client.send_message(chat_id, "⌯ حدث خطأ أثناء جلب الصورة.")
        print("⌯ خطأ في عشوائي:", e)