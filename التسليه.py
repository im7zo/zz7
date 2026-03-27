from config import client
import asyncio
import random
import string
import re
from telethon import events

# قائمة لتخزين المستخدمين المقلدين
trad_users = set()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.الأوامر$'))
async def start_commands(event):
    try:
        await event.delete()  # حذف رسالة الأمر

        result = await client.inline_query("x3i3ibot", "sitting")
        
        if result:
            await result[0].click(event.chat_id)
        else:
            await event.respond("حـدث خـطأ")
    
    except Exception as e:
        await event.respond(f"حدث خطأ: {str(e)}")


@client.on(events.NewMessage(outgoing=True, pattern=r"\.تقليد"))
async def start_mimic(event):
    if not event.is_reply:
        await event.edit("↯︙يجب الرد على رسالة الشخص الذي تريد تقليده.")
        return
    replied = await event.get_reply_message()
    trad_users.add(replied.sender_id)
    await event.edit(f"⎙ بدأ تقليد هذا المستخدم: {replied.sender.first_name}")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.ايقاف التقليد"))
async def stop_mimic(event):
    if not event.is_reply:
        await event.edit("↯︙يجب الرد على رسالة الشخص لإيقاف تقليده.")
        return
    replied = await event.get_reply_message()
    trad_users.discard(replied.sender_id)
    await event.edit(f"⎙ تم إيقاف تقليد المستخدم: {replied.sender.first_name}")

@client.on(events.NewMessage())
async def mimic_messages(event):
    if event.sender_id in trad_users and not event.out:
        try:
            await client.send_message(event.chat_id, event.raw_text)
        except Exception as e:
            print(f"حدث خطأ أثناء تقليد الرسالة: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.زواج"))
async def zawaj(event):
    if event.is_reply:
        replied = await event.get_reply_message()
        name = replied.sender.first_name
        await event.edit(f"💍 تم زواجك من {name} 👰‍♂️\nمنك المال ومنها العيال")
    else:
        await event.edit("↯︙يجب الرد على رسالة الشخص الذي تريد الزواج منه.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.طلاك"))
async def talaq(event):
    if event.is_reply:
        replied = await event.get_reply_message()
        name = replied.sender.first_name
        await event.edit(f"💔 تم طلاقك من {name}.\nنتمنى لك حياة أفضل")
    else:
        await event.edit("↯︙يجب الرد على رسالة الشخص الذي تريد تطليقه.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.نسبة (.+)"))
async def nesba(event):
    text = event.pattern_match.group(1)
    percent = random.randint(0, 100)
    await event.edit(f"نسبة {text} هي {percent}%")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.نسبتنا (.+)"))
async def nesbatna(event):
    text = event.pattern_match.group(1)
    percent = random.randint(0, 100)
    await event.edit(f"نسبتنا في {text} هي {percent}%")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اكس او$'))
async def start_xo(event):
    try:
        await event.delete()  # حذف رسالة الأمر
        result = await client.inline_query("xoBot", "play")
        if result:
            await result[0].click(event.chat_id)
        else:
            await event.respond("ما قدرنا نحصل على نتائج من @xoBot.")
    except Exception as e:
        await event.respond(f"حدث خطأ: {str(e)}")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.بوسة"))
async def bosa(event):
    if event.is_reply:
        replied = await event.get_reply_message()
        if replied.sender:
            user_id = replied.sender_id
            name = replied.sender.first_name or "شخص"
            mention = f"[{name}](tg://user?id={user_id})"
            await event.edit(f"💋 أرسل بوسة إلى {mention}")
        else:
            await event.edit("↯︙ما قدرت اجيب معلومات الشخص.")
    else:
        await event.edit("↯︙يجب الرد على رسالة الشخص الذي تريد تبوسه.")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ايميل وهمي'))
async def fake_email(event):
    user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = user + '@gmail.com'
    await event.edit(f"📩 تم إنشاء بريد وهمي:\n`{email}`\n(من عمكم بنيامين)")