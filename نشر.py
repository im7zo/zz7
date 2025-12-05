from config import client
import asyncio
import re
from telethon import events

# متغير تحكم عام لإيقاف النشر التلقائي
final = False

# ───────────── نشر برسالة محددة إلى مجموعات معينة ─────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر (\d+) (@?\S+)$"))
async def final_handler(event):
    await event.delete()
    parameters = re.split(r'\s+', event.text.strip(), maxsplit=2)
    if len(parameters) != 3:
        return await event.reply("يجب استخدام كتابة صحيحة، الرجاء التأكد من الأمر أولاً.")
    
    seconds = int(parameters[1])
    chat_usernames = parameters[2].split()
    global final
    final = True

    message = await event.get_reply_message()
    if not message:
        return await event.reply("يجب الرد على رسالة للنشر.")

    for chat_username in chat_usernames:
        try:
            chat = await client.get_entity(chat_username)
            await final_nshr(client, seconds, chat.id, message, seconds)
        except Exception as e:
            await event.reply(f"لا يمكن العثور على المجموعة أو الدردشة {chat_username}: {str(e)}")
        await asyncio.sleep(1)

async def final_nshr(client, sleeptimet, chat_id, message, seconds):
    global final
    while final:
        try:
            if message.media:
                await client.send_file(chat_id, message.media, caption=message.text)
            else:
                await client.send_message(chat_id, message.text)
        except Exception as e:
            print(f"Error sending to chat {chat_id}: {e}")
        await asyncio.sleep(sleeptimet)

# ───────────── نشر لجميع الكروبات ─────────────
async def final_allnshr(client, sleeptimet, message):
    global final
    final = True
    final_chats = await client.get_dialogs()
    while final:
        for chat in final_chats:
            if chat.is_group:
                try:
                    if message.media:
                        await client.send_file(chat.id, message.media, caption=message.text)
                    else:
                        await client.send_message(chat.id, message.text)
                except Exception as e:
                    print(f"Error in sending message to chat {chat.id}: {e}")
        await asyncio.sleep(sleeptimet)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر_كروبات (\d+)$"))
async def final_handler_all_groups(event):
    await event.delete()
    try:
        sleeptimet = int(event.pattern_match.group(1))
    except Exception:
        return await event.reply("يجب استخدام كتابة صحيحة، الرجاء التأكد من الأمر أولاً.")

    message = await event.get_reply_message()
    if not message:
        return await event.reply("يجب الرد على رسالة للنشر.")
    
    global final
    final = True
    await final_allnshr(client, sleeptimet, message)

# ───────────── نشر في مجموعات سوبر ─────────────
super_groups = ["super", "سوبر"]

async def final_supernshr(client, sleeptimet, message):
    global final
    final = True
    final_chats = await client.get_dialogs()
    while final:
        for chat in final_chats:
            if chat.is_group and any(keyword in chat.title.lower() for keyword in super_groups):
                try:
                    if message.media:
                        await client.send_file(chat.id, message.media, caption=message.text)
                    else:
                        await client.send_message(chat.id, message.text)
                except Exception as e:
                    print(f"Error in sending message to chat {chat.id}: {e}")
        await asyncio.sleep(sleeptimet)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سوبر (\d+)$"))
async def final_handler_super(event):
    await event.delete()
    try:
        sleeptimet = int(event.pattern_match.group(1))
    except Exception:
        return await event.reply("يجب استخدام كتابة صحيحة، الرجاء التأكد من الأمر أولاً.")
    
    message = await event.get_reply_message()
    if not message:
        return await event.reply("يجب الرد على رسالة للنشر.")
    
    global final
    final = True
    await final_supernshr(client, sleeptimet, message)

# ───────────── إيقاف النشر التلقائي ─────────────
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ايقاف النشر$'))
async def stop_final(event):
    global final
    final = False
    await event.edit("**⌯ تم إيقاف النشر التلقائي بنجاح ⌯**")

# ───────────── سبام بالكلمات ─────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وسبام$"))
async def word_spam_handler(event):
    await event.delete()
    message = await event.get_reply_message()
    if not message or not message.text:
        return await event.reply("يجب الرد على رسالة نصية لاستخدام هذا الأمر.")
    
    words = message.text.split()
    for word in words:
        await event.respond(word)
        await asyncio.sleep(1)

# ───────────── النشر بالتناوب ─────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تناوب (\d+)$"))
async def rotate_handler(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1))
    message = await event.get_reply_message()
    if not message:
        return await event.reply("يجب الرد على رسالة لاستخدام هذا الأمر.")

    global final
    final = True
    chats = await client.get_dialogs()
    groups = [chat for chat in chats if chat.is_group]
    if not groups:
        return await event.reply("لا توجد مجموعات للنشر فيها.")

    num_groups = len(groups)
    current_group_index = 0
    while final:
        try:
            if message.media:
                await client.send_file(groups[current_group_index].id, message.media, caption=message.text)
            else:
                await client.send_message(groups[current_group_index].id, message.text)
        except Exception as e:
            print(f"Error in sending message to chat {groups[current_group_index].id}: {e}")
        current_group_index = (current_group_index + 1) % num_groups
        await asyncio.sleep(seconds)

# ───────────── نشر للخاص ─────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.خاص$"))
async def private_handler(event):
    await event.delete()
    message = await event.get_reply_message()
    if not message:
        return await event.reply("يجب الرد على رسالة لاستخدام هذا الأمر.")

    chats = await client.get_dialogs()
    private_chats = [chat for chat in chats if chat.is_user]
    for chat in private_chats:
        try:
            if message.media:
                await client.send_file(chat.id, message.media, caption=message.text)
            else:
                await client.send_message(chat.id, message.text)
        except Exception as e:
            print(f"Error in sending message to chat {chat.id}: {e}")

# ───────────── نقط متكرر ─────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نقط (\d+)$"))
async def dot_handler(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1))
    reply_to_msg = await event.get_reply_message()
    if not reply_to_msg:
        return await event.reply("يجب الرد على رسالة لاستخدام هذا الأمر.")

    global final
    final = True
    while final:
        await reply_to_msg.reply(".")
        await asyncio.sleep(seconds)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مكرر (\d+)$"))
async def repeat_handler(event):
    await event.delete()
    seconds = int(event.pattern_match.group(1))
    message = await event.get_reply_message()
    if not message:
        return await event.reply("يجب الرد على رسالة لاستخدام هذا الأمر.")

    global final
    final = True
    while final:
        await message.respond(message.text if not message.media else message)
        await asyncio.sleep(seconds)