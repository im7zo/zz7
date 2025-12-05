from config import client
import asyncio
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon.tl.types import ChannelParticipantsAdmins

spam_chats = []

async def is_me(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def send_saved(text):
    """ترسل رسالة في Saved Messages وتُرجع الرسالة لتعديلها لاحقًا"""
    return await client.send_message("me", text)

async def process_members(event, action_type="حظر", check_bot=False):
    """
    action_type: "حظر" / "كتم" / "بوت"
    check_bot: True إذا أردنا طرد البوتات فقط
    """
    await event.delete()  # حذف أمر المستخدم فورًا
    chat_id = event.chat_id

    try:
        await client(GetParticipantRequest(chat_id, event.sender_id))
    except UserNotParticipantError:
        pass

    spam_chats.append(chat_id)
    participants = [usr async for usr in client.iter_participants(chat_id)]
    total = len(participants)
    success = 0

    counter_msg = await send_saved(
        f"تـم {action_type} {success} عـضـو مـن {total} .. بنجــاح✓"
    )

    admins = [i.id async for i in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins)]

    for usr in participants:
        if chat_id not in spam_chats:
            break
        if check_bot and not getattr(usr, "bot", False):
            continue
        if not check_bot and usr.id in admins:
            continue

        success += 1
        username = getattr(usr, "username", None)
        display_name = f"@{username}" if username else str(usr.id)

        if action_type == "حظر":
            await client.send_message(chat_id, f"حظر {display_name}")
        elif action_type == "كتم":
            await client.send_message(chat_id, f"كتم {display_name}")
        elif action_type == "بوت":
            await client.send_message(chat_id, f"تم طرد البوت {display_name}")

        await counter_msg.edit(
            f"تـم {action_type} {success} عـضـو مـن {total} .. بنجــاح✓"
        )
        await asyncio.sleep(0.5)

    if chat_id in spam_chats:
        spam_chats.remove(chat_id)

# ----- أوامر التفليش والكتم والبوتات -----
@client.on(events.NewMessage(pattern=r"\.تفليش بالبوت$", chats=None))
async def flash_bot(event):
    if not await is_me(event):
        return
    await process_members(event, action_type="حظر")

@client.on(events.NewMessage(pattern=r"\.كتم الكل$", chats=None))
async def mute_all(event):
    if not await is_me(event):
        return
    await process_members(event, action_type="كتم")

@client.on(events.NewMessage(pattern=r"\.ازالة البوتات$", chats=None))
async def remove_bots(event):
    if not await is_me(event):
        return

    await event.delete()  
    chat_id = event.chat_id

    participants = [usr async for usr in client.iter_participants(chat_id)]
    bots = [usr for usr in participants if getattr(usr, "bot", False)]
    total = len(bots)
    success = 0

    if total == 0:
        await send_saved("لا يـوجـد أي بـوتـات فـي المجـموعـة")
        return

    counter_msg = await send_saved(
        f"تـم طـرد {success} بـوت مـن {total} .. بنجـاح ✓"
    )

    for usr in bots:
        try:
            await client.kick_participant(chat_id, usr.id)
            success += 1
            await counter_msg.edit(
                f"تـم طـرد {success} بـوت مـن {total} .. بنجـاح ✓"
            )
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"خطأ مع {usr.id}: {e}")
            continue

# ----- إيقاف التفليش -----
@client.on(events.NewMessage(pattern=r"\.الغاء التفليش$", chats=None))
async def stop_flash(event):
    if not await is_me(event):
        return
    await event.delete()
    if event.chat_id not in spam_chats:
        await send_saved("**- لاتوجـد عمليـة تفليـش هنـا لـ إيقافـها ؟!**")
        return
    spam_chats.remove(event.chat_id)
    await send_saved("**تـم إيـقـاف عمليـة التفليـش .. بنجـاح✓**")

@client.on(events.NewMessage(pattern=r"\.ايقاف التفليش$", chats=None))
async def stop_flash2(event):
    if not await is_me(event):
        return
    await event.delete()
    if event.chat_id not in spam_chats:
        await send_saved("**- لاتوجـد عمليـة تفليـش هنـا لـ إيقافـها ؟!**")
        return
    spam_chats.remove(event.chat_id)
    await send_saved("**تـم إيـقـاف عمليـة التفليـش .. بنجـاح✓**")