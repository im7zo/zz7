from config import client
import os
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError

# مسارات الملفات
channel_file = "forced_channel.txt"
join_msg_file = "join_message.txt"

# الكليشة الافتراضية عند عدم الاشتراك
DEFAULT_JOIN_MSG = """⌯ لا يمكنك مراسلتي.

اشترك بالقناة ثم ارجع ارسل رسالتك:
https://t.me/{channel}
"""

# -------------------------
# أمر: .اضافة قناة
# -------------------------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اضافة قناة(?: (.+))?$'))
async def add_forced_channel(event):
    input_channel = event.pattern_match.group(1)
    if not input_channel:
        return await event.edit("❗اسـتـخـدم الامـر هـكذا \n`.اضافة قناة @YourChannel`")

    with open(channel_file, "w") as f:
        f.write(input_channel.strip().replace("@", ""))

    await event.edit(f"تـم تفـعيـل الاشتـراك الاجـبـاري\n@{input_channel.strip().replace('@','')}")

# -------------------------
# أمر: .حذف قناة
# -------------------------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.حذف قناة$'))
async def remove_forced_channel(event):
    if os.path.exists(channel_file):
        os.remove(channel_file)
        await event.edit("تـم حـذف الاشتـراك الاجـبـاري")
    else:
        await event.edit("❗ لا يـوجـد اشتـراك اجـبـاري مـفعل حـاليًـا")

# -------------------------
# أمر: .تعيين كليشة الاشتراك
# -------------------------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعيين كليشة الاشتراك$'))
async def set_join_message(event):
    if not event.is_reply:
        return await event.edit("❗يـجـب الـرد علـى رسـالة تـحـتوي كليـشة الاشـتـراك")

    reply = await event.get_reply_message()
    text = reply.text or reply.message or ""
    if not text:
        return await event.edit("❗الـرسـالة التـي رددت علـيها فـارغـة")

    # قراءة القناة المخزّنة
    if os.path.exists(channel_file):
        with open(channel_file, "r") as f:
            channel_username = f.read().strip()
    else:
        return await event.edit("❗ يـجـب تعـيين قـناة الإشـتـراك اولا\n`.اضافة قناة @yourchannel`")

    # إضافة رابط القناة تلقائياً تحت النص
    final_text = text + f"\nhttps://t.me/{channel_username}"

    with open(join_msg_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    await event.edit("تـم تعـيين كليـشة الإشـتـراك")

# -------------------------
# أمر: .حذف كليشة الاشتراك
# -------------------------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.حذف كليشة الاشتراك$'))
async def delete_join_message(event):
    if os.path.exists(join_msg_file):
        os.remove(join_msg_file)
        await event.edit("تـم حـذف كليـشة الاشـتـراك")
    else:
        await event.edit("❗ لا تـوجـد كليـشة اشـتـراك محـفوظـة")

# -------------------------
# فحص الاشتراك عند أي رسالة واردة بالخاص
# -------------------------
@client.on(events.NewMessage(incoming=True))
async def check_private(event):
    if not event.is_private:
        return

    sender = await event.get_sender()

    # تجاهل البوتات
    if sender.bot:
        return

    # إذا ماكو قناة اشتراك إجباري → خروج
    if not os.path.exists(channel_file):
        return

    with open(channel_file, "r") as f:
        channel_username = f.read().strip()

    try:
        # فحص إذا الشخص مشترك في القناة
        await client(GetParticipantRequest(
            channel=channel_username,
            participant=sender.id
        ))
        # لو مشترك → خليه يرسل طبيعي
    except UserNotParticipantError:
        # تحميل كليشة الاشتراك
        if os.path.exists(join_msg_file):
            with open(join_msg_file, "r", encoding="utf-8") as f:
                join_msg = f.read()
        else:
            join_msg = DEFAULT_JOIN_MSG.format(channel=channel_username)

        # إرسال الكليشة
        await event.reply(join_msg)

        # حذف رسالة الشخص
        try:
            await event.delete()
        except:
            pass