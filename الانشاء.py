import re
from telethon import events
from config import client

TARGET_BOT = "@TGDNAbot"

@client.on(events.NewMessage(outgoing=True, pattern=r"\.الانشاء(?:\s+(.+))?"))
async def account_create(event):
    user = event.pattern_match.group(1)

    async with client.conversation(TARGET_BOT, timeout=20) as conv:
        try:
            # إرسال الأمر أو اليوزر
            if not user:
                await conv.send_message("/start")
            else:
                await conv.send_message(user)

            # تجاهل أول رسالة فقط إذا الأمر بدون يوزر
            if not user:
                await conv.get_response()  # الرسالة الأولى → تجاهل

            # أخذ الرسالة التالية من البوت
            msg = await conv.get_response()
            text = msg.raw_text

            # إذا الأمر بدون يوزر → حذف - /start
            if not user:
                text = re.sub(r"^- /start\s*$", "", text, flags=re.MULTILINE).strip()

            # تعديل نفس رسالة الأمر
            await event.edit(text)

        except Exception as e:
            await event.edit(f"❌ حدث خطأ: {e}")

    # حذف المحادثة مع البوت
    try:
        await client.delete_dialog(TARGET_BOT)
    except:
        pass