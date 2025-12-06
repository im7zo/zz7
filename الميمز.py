from config import client
from telethon import events
from telethon.tl.types import MessageMediaDocument, DocumentAttributeAudio

sad_channel = '@zzio5'  # غيّرها حسب اسم قناتك

def is_audio(msg):
    if not msg:
        return False
    if msg.voice or msg.audio:
        return True
    if isinstance(msg.media, MessageMediaDocument):
        attrs = msg.media.document.attributes
        for attr in attrs:
            if isinstance(attr, DocumentAttributeAudio):
                return True
    return False

async def send_audio_by_msg_id(event, msg_id):
    try:
        reply_to_msg_id = event.reply_to_msg_id or event.message.id
        await event.delete()  # حذف الأمر فورًا
        msg = await client.get_messages(sad_channel, ids=msg_id)
        if msg and is_audio(msg):
            await client.send_file(event.chat_id, msg, reply_to=reply_to_msg_id)
        else:
            await client.send_message(event.chat_id, "↯ ما لقيت صوت بالرسالة.", reply_to=reply_to_msg_id)
    except Exception as e:
        await client.send_message(event.chat_id, f"✗ خطأ: {e}", reply_to=reply_to_msg_id)

# --- أوامر البصمات ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اغمضتها$'))
async def memez_1(event):
    await send_audio_by_msg_id(event, 358)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.هزيمه مؤلمة$'))
async def memez_2(event):
    await send_audio_by_msg_id(event, 116)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.زيج حزين$'))
async def memez_3(event):
    await send_audio_by_msg_id(event, 117)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ما يهمني$'))
async def memez_4(event):
    await send_audio_by_msg_id(event, 115)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.لعنه امون$'))
async def memez_5(event):
    await send_audio_by_msg_id(event, 114)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ضحك 1$'))
async def memez_6(event):
    await send_audio_by_msg_id(event, 113)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ضحك 2$'))
async def memez_7(event):
    await send_audio_by_msg_id(event, 112)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.خناجر$'))
async def memez_8(event):
    await send_audio_by_msg_id(event, 111)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.خابرني عاليوتيوب$'))
async def memez_9(event):
    await send_audio_by_msg_id(event, 110)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ام لولي$'))
async def memez_10(event):
    await send_audio_by_msg_id(event, 109)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اشك هدومي$'))
async def memez_11(event):
    await send_audio_by_msg_id(event, 108)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.زيج$'))
async def memez_12(event):
    await send_audio_by_msg_id(event, 118)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اكل خرا$'))
async def memez_13(event):
    await send_audio_by_msg_id(event, 119)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.كزاب$'))
async def memez_14(event):
    await send_audio_by_msg_id(event, 681)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.السيدي$'))
async def memez_15(event):
    await send_audio_by_msg_id(event, 682)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.خيار بصل$'))
async def memez_16(event):
    await send_audio_by_msg_id(event, 683)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.مو مطي$'))
async def memez_17(event):
    await send_audio_by_msg_id(event, 684)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.انلاصت$'))
async def memez_18(event):
    await send_audio_by_msg_id(event, 685)