import random
from telethon import events
from config import client

@client.on(events.NewMessage(pattern=r"^\.فلم$"))
async def movie_handler(event):
    me = await client.get_me()
    if event.sender_id != me.id:  # فقط الرسائل الصادرة منك
        return

    channel = "@zzio5"
    start_id = 567
    end_id = 658

    await event.edit("انتظر . . .")
    messages = []
    async for msg in client.iter_messages(channel, min_id=start_id, max_id=end_id):
        if msg.photo and msg.text:
            messages.append(msg)

    if messages:
        chosen = random.choice(messages)
        await event.edit(file=chosen.photo, text=chosen.text)
    else:
        await event.edit("هنـالك خطـأ غـير متـوقع حـاول لاحقًـا")