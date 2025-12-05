import os
import random
from telethon import events
from config import client  # استيراد client من ملف config

# ==========================
# إعدادات القنوات والملفات
# ==========================
AVATAR_CHANNEL = "@zzio5"
ZM_CHANNEL = "@zzio5"
QURAN_CHANNEL = "@zzio5"

# ==========================
# حذف الأمر والرد عليه
# ==========================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.مسح$'))
async def delete_reply_and_command(event):
    try:
        await event.delete()
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            await reply_msg.delete()
    except Exception as e:
        print(f"خطأ أثناء الحذف: {e}")

# ==========================
# المراقبة والتفعيل/التعطيل
# ==========================
dua_enabled_groups = set()
poetry_enabled_groups = set()
quran_enabled_groups = set()

# تفعيل / تعطيل الدعاء
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تفعيل الدعاء$'))
async def enable_dua(event):
    if event.is_group:
        dua_enabled_groups.add(event.chat_id)
        await event.edit("تـم تفـعيل إرسـال الـدعاء عنـد كتـابة ، **دعاء**")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعطيل الدعاء$'))
async def disable_dua(event):
    if event.is_group:
        dua_enabled_groups.discard(event.chat_id)
        await event.edit("تـم تعـطيل إرسـال الـدعاء فـي هـذهِ المـجمـوعة")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")


# تفعيل / تعطيل الشعر
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تفعيل الشعر$'))
async def enable_poetry(event):
    if event.is_group:
        poetry_enabled_groups.add(event.chat_id)
        await event.edit("تـم تفـعيل إرسـال الـشـعر عنـد كتـابة ، **شعر**")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعطيل الشعر$'))
async def disable_poetry(event):
    if event.is_group:
        poetry_enabled_groups.discard(event.chat_id)
        await event.edit("تـم تعـطيل إرسـال الـشـعر فـي هـذهِ المـجمـوعة")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")


# تفعيل / تعطيل القرآن
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تفعيل القران$'))
async def enable_quran(event):
    if event.is_group:
        quran_enabled_groups.add(event.chat_id)
        await event.edit("تـم تفـعيل إرسـال الـقـرآن عنـد كتـابة ، **قران**'")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعطيل القران$'))
async def disable_quran(event):
    if event.is_group:
        quran_enabled_groups.discard(event.chat_id)
        await event.edit("تـم تعـطيل إرسـال الـقـرآن فـي هـذهِ المـجمـوعة")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.دعاء$'))
async def manual_dua(event):
    try:
        await event.delete()
        msg_id = random.randint(686, 694)
        msg = await client.get_messages(ZM_CHANNEL, ids=msg_id)

        if msg and msg.media:
            await client.send_file(event.chat_id, msg)
        else:
            await event.respond("⌯ لم أجد دعاء متاح")
    except Exception as e:
        await event.respond(f"⌯ حدث خطأ: {e}")


# ==========================
# 📌 شعر يدوي
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.شعر$'))
async def manual_poetry(event):
    try:
        await event.delete()
        msg_id = random.randint(720, 780 )
        msg = await client.get_messages(ZM_CHANNEL, ids=msg_id)

        if msg and msg.media:
            await client.send_file(event.chat_id, msg)
        else:
            await event.respond("⌯ لم أجد شعر متاح")
    except Exception as e:
        await event.respond(f"⌯ حدث خطأ: {e}")


# ==========================
# 📌 قصيدة
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.قصيدة$'))
async def manual_qasida(event):
    try:
        await event.delete()
        msg_id = random.randint(121, 320)
        msg = await client.get_messages(ZM_CHANNEL, ids=msg_id)

        if msg and (msg.audio or msg.voice):
            await client.send_file(event.chat_id, msg)
        else:
            await event.respond("⌯ لم أجد قصيدة متاحة")
    except Exception as e:
        await event.respond(f"⌯ حدث خطأ: {e}")


# ==========================
# 📌 قرآن
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.قران$'))
async def manual_quran(event):
    try:
        await event.delete()
        msg_id = random.randint(8, 107)
        msg = await client.get_messages(QURAN_CHANNEL, ids=msg_id)

        if msg and msg.audio:
            await client.send_file(event.chat_id, msg)
        else:
            await event.respond("↯ لم أجد مقطع صوتي في الرسالة، حاول مرة أخرى.")
    except Exception as e:
        await event.respond(f"⚠️ حدث خطأ: {e}")


# ==========================
# المراقبة التلقائية
# ==========================
@client.on(events.NewMessage(outgoing=True))
async def auto_dua(event):
    if event.is_group and event.chat_id in dua_enabled_groups:
        text = event.raw_text.lower()
        if text.startswith("."):
            return
        if "دعاء" in text:
            try:
                msg_id = random.randint(686, 694)
                msg = await client.get_messages(ZM_CHANNEL, ids=msg_id)
                if msg and msg.media and hasattr(msg.media, 'document'):
                    await client.send_file(event.chat_id, msg, reply_to=event.id)
            except:
                pass


@client.on(events.NewMessage(outgoing=True))
async def auto_poetry(event):
    if event.is_group and event.chat_id in poetry_enabled_groups:
        text = event.raw_text.lower()
        if text.startswith("."):
            return
        if "شعر" in text:
            try:
                msg_id = random.randint(720, 780)
                msg = await client.get_messages(ZM_CHANNEL, ids=msg_id)
                if msg and msg.media and hasattr(msg.media, 'document'):
                    await client.send_file(event.chat_id, msg, reply_to=event.id)
            except:
                pass


@client.on(events.NewMessage(outgoing=True))
async def auto_quran(event):
    if event.is_group and event.chat_id in quran_enabled_groups:
        text = event.raw_text.lower()
        if text.startswith("."):
            return
        if "قران" in text:
            try:
                msg_id = random.randint(8, 107)
                msg = await client.get_messages(QURAN_CHANNEL, ids=msg_id)
                if msg and msg.audio:
                    await client.send_file(event.chat_id, msg.audio, reply_to=event.id)
            except:
                pass