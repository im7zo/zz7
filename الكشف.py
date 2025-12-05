from telethon import TelegramClient, events, sync
from telethon.errors import rpcbaseerrors
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, CheckChatInviteRequest, GetFullChatRequest
from telethon.tl.types import MessageActionChannelMigrateFrom, ChannelParticipantsAdmins, Channel, Chat, User
from telethon.errors import (
    ChannelInvalidError, ChannelPrivateError, ChannelPublicGroupNaError,
    InviteHashEmptyError, InviteHashExpiredError, InviteHashInvalidError
)
from telethon.utils import get_input_location
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from math import sqrt
from datetime import datetime
import os

# استيراد client من config
from config import client

# ─── 1. كشف المجموعة ─────────────────────────────
@client.on(events.NewMessage(pattern=r"^\.كشف المجموعة(?: |$)(.*)", outgoing=True))
async def info_gop(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    await event.edit("جارٍ الفحص ...")
    chat = await get_chatinfo(event)
    caption = await fetch_info(chat, event)
    try:
        await event.edit(caption, parse_mode="html")
    except Exception as e:
        print("Exception:", e)
        await event.edit("حدث خطأ غير متوقع.")
    return

async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.edit("حدث خطأ في القناة أو المجموعة..")
            return None
        except ChannelPrivateError:
            await event.edit("هذه قناة/مجموعة خاصة أو تم حظري منها")
            return None
        except ChannelPublicGroupNaError:
            await event.edit("القناة أو المجموعة غير موجودة")
            return None
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None
    return chat_info

async def fetch_info(chat, event):
    chat_obj_info = await event.client.get_entity(chat.full_chat.id)
    broadcast = getattr(chat_obj_info, "broadcast", False)
    chat_type = "قناة" if broadcast else "مجموعة"
    chat_title = chat_obj_info.title

    try:
        msg_info = await event.client(GetHistoryRequest(
            peer=chat_obj_info.id,
            offset_id=0, offset_date=datetime(2010, 1, 1),
            add_offset=-1, limit=1, max_id=0, min_id=0, hash=0
        ))
    except Exception as e:
        msg_info = None
        print("Exception:", e)

    first_msg_valid = bool(msg_info and msg_info.messages and msg_info.messages[0].id == 1)
    creator_valid = bool(first_msg_valid and msg_info.users)
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = msg_info.users[0].first_name if creator_valid and msg_info.users[0].first_name else "حساب محذوف"
    creator_username = msg_info.users[0].username if creator_valid and msg_info.users[0].username else None
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = (msg_info.messages[0].action.title
                    if first_msg_valid and isinstance(msg_info.messages[0].action, MessageActionChannelMigrateFrom)
                    and msg_info.messages[0].action.title != chat_title else None)
    try:
        dc_id, location = get_input_location(chat.full_chat.chat_photo)
    except Exception as e:
        dc_id = "غير معروف"
        location = str(e)

    description = chat.full_chat.about
    members = getattr(chat.full_chat, "participants_count", getattr(chat_obj_info, "participants_count", None))
    admins = getattr(chat.full_chat, "admins_count", None)
    banned_users = getattr(chat.full_chat, "kicked_count", None)
    restrcited_users = getattr(chat.full_chat, "banned_count", None)
    members_online = getattr(chat.full_chat, "online_count", 0)
    group_stickers = chat.full_chat.stickerset.title if getattr(chat.full_chat, "stickerset", None) else None
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = getattr(chat.full_chat, "read_inbox_max_id", None)
    messages_sent_alt = getattr(chat.full_chat, "read_outbox_max_id", None)
    exp_count = getattr(chat.full_chat, "pts", None)
    username = getattr(chat_obj_info, "username", None)
    bots_list = chat.full_chat.bot_info
    bots = len(bots_list) if bots_list else 0
    supergroup = "نعم" if getattr(chat_obj_info, "megagroup", False) else "لا"
    slowmode = "نعم" if getattr(chat_obj_info, "slowmode_enabled", False) else "لا"
    slowmode_time = getattr(chat.full_chat, "slowmode_seconds", None)
    restricted = "نعم" if getattr(chat_obj_info, "restricted", False) else "لا"
    verified = "نعم" if getattr(chat_obj_info, "verified", False) else "لا"
    username = f"@{username}" if username else None
    creator_username = f"@{creator_username}" if creator_username else None

    if admins is None:
        try:
            participants_admins = await event.client(GetParticipantsRequest(
                channel=chat.full_chat.id, filter=ChannelParticipantsAdmins(),
                offset=0, limit=0, hash=0
            ))
            admins = participants_admins.count if participants_admins else None
        except Exception as e:
            print("Exception:", e)

    caption = "المعلومات المتاحة:\n"
    caption += f"المعرف: {chat_obj_info.id}\n"
    if chat_title:
        caption += f"اسم {chat_type}: {chat_title}\n"
    if former_title:
        caption += f"الاسم السابق: {former_title}\n"
    if username:
        caption += f"نوع {chat_type}: عامة\nالرابط: {username}\n"
    else:
        caption += f"نوع {chat_type}: خاصة\n"
    if creator_username:
        caption += f"منشئ {chat_type}: {creator_username}\n"
    elif creator_valid:
        caption += f"منشئ {chat_type}: https://t.me/{creator_id}\n"
    if created:
        caption += f"تاريخ الإنشاء: {created.date().strftime('%b %d, %Y')} - {created.time()}\n"
    else:
        caption += f"تاريخ الإنشاء: {chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}\n"
    caption += f"معرف مركز البيانات: {dc_id}\n"
    if exp_count:
        chat_level = int((1 + sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f"مستوى {chat_type}: {chat_level}\n"
    if messages_viewable is not None:
        caption += f"الرسائل القابلة للعرض: {messages_viewable}\n"
    if messages_sent:
        caption += f"الرسائل المرسلة: {messages_sent}\n"
    elif messages_sent_alt:
        caption += f"الرسائل المرسلة: {messages_sent_alt}\n"
    if members is not None:
        caption += f"الأعضاء: {members}\n"
    if admins is not None:
        caption += f"المشرفون: {admins}\n"
    if bots_list:
        caption += f"البوتات: {bots}\n"
    if members_online:
        caption += f"الأعضاء المتصلون الآن: {members_online}\n"
    if restrcited_users is not None:
        caption += f"الأعضاء المقيدون: {restrcited_users}\n"
    if banned_users is not None:
        caption += f"الأعضاء المحظورون: {banned_users}\n"
    if group_stickers:
        caption += f"ملصقات {chat_type}: https://t.me/addstickers/{chat.full_chat.stickerset.short_name}\n"
    caption += "\n"
    if not broadcast:
        caption += f"الوضع البطيء: {slowmode}"
        if getattr(chat_obj_info, "slowmode_enabled", False):
            caption += f", {slowmode_time}s\n\n"
        else:
            caption += "\n\n"
    if not broadcast:
        caption += f"مجموعة عملاقة: {supergroup}\n\n"
    if hasattr(chat_obj_info, "restricted"):
        caption += f"مقيد: {restricted}\n"
        if chat_obj_info.restricted:
            caption += f"> المنصة: {chat_obj_info.restriction_reason[0].platform}\n"
            caption += f"> السبب: {chat_obj_info.restriction_reason[0].reason}\n"
            caption += f"> النص: {chat_obj_info.restriction_reason[0].text}\n\n"
        else:
            caption += "\n"
    if getattr(chat_obj_info, "scam", False):
        caption += "احتيال: نعم\n\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"تم التحقق منه بواسطة Telegram: {verified}\n\n"
    if description:
        caption += f"الوصف: \n{description}\n"
    return caption

# ─── 2. كشف الحساب ─────────────────────────────
@client.on(events.NewMessage(pattern=r"^\.كشف الحساب$", outgoing=True))
async def account_summary(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    await event.delete()
    me = await client.get_me()
    total_channels = total_groups = total_bots = total_chats = 0

    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel):
            if entity.megagroup:
                total_groups += 1
            else:
                total_channels += 1
        elif isinstance(entity, Chat):
            total_groups += 1
        elif isinstance(entity, User):
            total_chats += 1
            if entity.bot:
                total_bots += 1

    photos = await client(GetUserPhotosRequest(
        user_id=me.id, offset=0, max_id=0, limit=100
    ))
    total_photos = len(photos.photos)

    msg = f"""•⎚• كشـف الحـساب من سـورس 𝐙

✦ عدد القنوات: {total_channels}
✦ عدد الكروبات: {total_groups}
✦ عدد البوتات: {total_bots}
✦ عدد المحادثات: {total_chats}
✦ عدد صور الحساب: {total_photos}
"""
    await event.respond(msg)

# ─── 3. كشف معلومات مستخدم ─────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف(?! الحساب| المجموعة)(?: (.+))?$"))
async def whois(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    input_str = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    user = None

    try:
        if input_str:
            try:
                user = await client.get_entity(input_str)
            except Exception:
                return await event.edit("الرجاء إدخال معرف مستخدم صالح أو الرد على رسالة شخص.")
        elif reply:
            user = await reply.get_sender()
        else:
            user = await event.get_sender()

        full = await client(GetFullUserRequest(user.id))

        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد"
        link = f"https://t.me/{user.username}" if user.username else "لا يوجد"
        user_id = user.id
        created_at = getattr(user, "date", None)
        created_at_str = created_at.strftime("%Y-%m-%d") if created_at else "غير معروف"

        status = getattr(user.status, "__class__", type("Unknown", (), {})).__name__
        last_seen = {
            "UserStatusRecently": "مؤخراً",
            "UserStatusOnline": "متصل الآن",
            "UserStatusOffline": "غير متصل",
            "UserStatusLastWeek": "الأسبوع الماضي",
            "UserStatusLastMonth": "الشهر الماضي"
        }.get(status, "غير معروف")

        caption = (
            f"معلومات المستخدم:\n"
            f"• الاسم: {name or 'لا يوجد'}\n"
            f"• اليوزر: {username}\n"
            f"• الآيدي: {user_id}\n"
            f"• الرابط: {link}\n"
            f"• تاريخ الإنشاء: {created_at_str}\n"
            f"• آخر ظهور: {last_seen}"
        )

        try:
            photo = await client.download_profile_photo(user, file="photo.jpg")
            await event.reply(file="photo.jpg", message=caption)
            os.remove("photo.jpg")
        except:
            await event.reply(caption)

    except Exception as e:
        await event.reply(f"تعذر جلب معلومات المستخدم:\n{e}")