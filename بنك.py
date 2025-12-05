from telethon import events
from config import client
from datetime import datetime

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بنك$'))
async def ping(event):
    client.parse_mode = "markdown"
    start = datetime.now()
    msg = await event.edit("⌯ سرعة الانترنيت!")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await msg.edit(f"**⌯ سرعة انترنيتك!!**\n`{ms} ms`")