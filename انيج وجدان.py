import os
import re
from telethon import events
from telethon.errors.rpcerrorlist import InviteHashExpiredError, InviteHashInvalidError
from telethon.tl.functions.channels import JoinChannelRequest, CreateChannelRequest
from telethon.tl.types import InputChannel
from config import client

CHANNEL_FILE = "wjdan_channel.txt"

async def get_or_create_channel():
    """
    ترجع ID قناة ست وجدان — أو تنشئها إذا ما موجودة
    """
    # إذا القناة موجودة مسبقًا
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r") as f:
            return int(f.read().strip())

    # إنشاء قناة جديدة
    result = await client(CreateChannelRequest(
        title="ست وجدان",
        about="قناة لحفظ محتوى القنوات الخاصة 📨",
        megagroup=False  # قناة
    ))

    channel = result.chats[0]
    channel_id = channel.id

    # حفظ ID
    with open(CHANNEL_FILE, "w") as f:
        f.write(str(channel_id))

    return channel_id


@client.on(events.NewMessage(outgoing=True, pattern=r"\.سحب محتوى القناة\s+(https?://t\.me/\S+)"))
async def scrape_private(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    link = event.pattern_match.group(1)
    msg = await event.edit("🔍 تجهيز قناة الحفظ...")

    # إنشاء قناة أو الحصول عليها
    target_id = await get_or_create_channel()

    try:
        # التحقق من رابط الدعوة الخاص
        if "+" in link or "joinchat" in link:
            try:
                await client(JoinChannelRequest(link))
            except InviteHashInvalidError:
                return await msg.edit("❌ رابط الدعوة غير صحيح")
            except InviteHashExpiredError:
                return await msg.edit("❌ رابط الدعوة منتهي")
        else:
            return await msg.edit("❌ هذا ليس رابط دعوة خاص")

        # بعد الانضمام — الحصول على الكيان
        entity = await client.get_entity(link)

        await msg.edit("📥 سحب المحتوى من القناة...")
        count = 0

        async for message in client.iter_messages(entity, reverse=True):
            try:
                # صور
                if message.photo:
                    file = await message.download_media()
                    await client.send_file(target_id, file, caption=message.message or "")
                    os.remove(file)
                    count += 1

                # نص فقط
                elif message.message and not message.media:
                    await client.send_message(target_id, message.message)
                    count += 1

            except:
                pass

        await msg.edit(f"✔️ تم إنشاء قناة (ست وجدان) وسحب {count} رسالة 📦")

    except Exception as e:
        await msg.edit(f"❌ خطأ غير متوقع: {e}")