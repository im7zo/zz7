import asyncio
from telethon import events
from config import client

auto_posts = {}  # chat_id: True/False

@client.on(events.NewMessage(pattern=r"\.ستارت (\d+) (\d+)"))
async def start_autopost(event):

    if not event.is_reply:
        msg = await event.edit("❗️يـجـب الـرد على رسـالة")
        await asyncio.sleep(0.5)
        await msg.delete()
        return

    chat_id = event.chat_id

    if auto_posts.get(chat_id):
        msg = await event.edit("⚠️ النـشر شـغال بهـالكـروب")
        await asyncio.sleep(0.5)
        await msg.delete()
        return

    seconds = int(event.pattern_match.group(1))
    times = int(event.pattern_match.group(2))

    reply_msg = await event.get_reply_message()

    auto_posts[chat_id] = True

    start_msg = await event.edit(
        f"**تـم بـدء النـشر التـلقائي ، ثواني : {seconds} | مرات : {times}**"
    )
    await asyncio.sleep(0.5)
    await start_msg.delete()

    for _ in range(times):
        if not auto_posts.get(chat_id):
            break

        await client.send_message(chat_id, reply_msg)
        await asyncio.sleep(seconds)

    auto_posts[chat_id] = False


@client.on(events.NewMessage(pattern=r"\.بس"))
async def stop_autopost(event):
    chat_id = event.chat_id

    if not auto_posts.get(chat_id):
        msg = await event.edit("⚠️ مـاكو نـشر شـغال هـنا")
        await asyncio.sleep(0.5)
        await msg.delete()
        return

    auto_posts[chat_id] = False

    stop_msg = await event.edit("⌯ تم إيقاف النشر التلقائي بنجاح ⌯")
    await asyncio.sleep(0.5)
    await stop_msg.delete()