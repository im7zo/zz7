import datetime
import time
import os
import json
import platform
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.channels import CreateChannelRequest, GetFullChannelRequest
from telethon.errors import ChannelInvalidError, ChannelPrivateError
from config import client, start_time

# ملفات الإعدادات
CONFIG_FILE = "config.json"
GROUPS_FILE = "groups.json"
DATA_FOLDER = "data"
F7_FILE = os.path.join(DATA_FOLDER, "f7.json")

os.makedirs(DATA_FOLDER, exist_ok=True)

from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest, GetFullChannelRequest
from telethon.errors import ChannelInvalidError, ChannelPrivateError

# تحميل وحفظ الإعدادات والمجموعات
def load_json_file(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

config = load_json_file(CONFIG_FILE, {"store_private": True, "store_groups": True})
groups = load_json_file(GROUPS_FILE, {})
f7_data = load_json_file(F7_FILE, {})

# التأكد من صلاحية القناة
async def is_group_valid(chat_id):
    try:
        await client(GetFullChannelRequest(chat_id))
        return True
    except (ChannelInvalidError, ChannelPrivateError):
        return False

# إنشاء مجموعة التخزين إذا لم تكن موجودة أو غير صالحة + إضافة صورة
async def create_storage_group():
    if "storage_chat_id" not in groups or not await is_group_valid(groups["storage_chat_id"]):
        result = await client(CreateChannelRequest(
            title="مجمـوعـة التخـزيـن",
            about="لا تقم بحذف هذه المجموعة أو التغيير إلى مجموعة عامـة (وظيفتهـا تخزيـن رسـائل الخـاص.)",
            megagroup=True
        ))
        groups["storage_chat_id"] = result.chats[0].id
        save_json_file(GROUPS_FILE, groups)

        # رفع صورة للمجموعة
        try:
            await client(EditPhotoRequest(
                channel=groups["storage_chat_id"],
                photo=await client.upload_file("mahd/Z.jpg")
            ))
        except Exception as e:
            print(f"⌔┊ فشل رفع صورة المجموعة: {e}")

# الأوامر
@client.on(events.NewMessage(pattern=r"^.تفعيل التخزين$"))
async def enable_storage(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    config["store_private"] = True
    config["store_groups"] = True
    save_json_file(CONFIG_FILE, config)

    await create_storage_group()

    await client.send_message(groups["storage_chat_id"],
                              "⌔┊ تم تفعيل التخزين من السورس\n⌔┊ By : @cfc_5\n⌔┊ 𝐒𝐎𝐔𝐑𝐂𝐄 𝐙  𝐓𝐎𝐏 1")
    await event.edit("⌔┊ تم تفعيل التخزين.")

@client.on(events.NewMessage(pattern=r"^.تعطيل التخزين$"))
async def disable_storage(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    config["store_private"] = False
    config["store_groups"] = False
    save_json_file(CONFIG_FILE, config)
    await event.edit("⌔┊ تم تعطيل التخزين.")

# تخزين رسائل الخاص
@client.on(events.NewMessage(incoming=True))
async def forward_private(event):
    if event.is_private and config.get("store_private", False):
        try:
            if "storage_chat_id" in groups:
                await client.forward_messages(groups["storage_chat_id"], event.message, event.sender_id)
        except Exception as e:
            print(f"⌔┊ فشل تحويل رسالة الخاص: {e}")

# تخزين تاكات الكروبات
@client.on(events.NewMessage(incoming=True))
async def forward_group_reply(event):
    if event.is_group and config.get("store_groups", False):
        if event.message.is_reply:
            try:
                replied = await event.get_reply_message()
                me = await client.get_me()

                # تحقق من وجود الرد ومرسله
                if replied and replied.sender_id == me.id:
                    chat = await event.get_chat()
                    sender = await event.get_sender()

                    # اسم المرسل كرابط
                    if sender and sender.id:
                        sender_name = f"[{sender.first_name}](tg://user?id={sender.id})"
                    else:
                        sender_name = "بدون اسم"

                    # رابط الرسالة
                    msg_link = (f"https://t.me/c/{str(event.chat_id)[4:]}/{event.id}"
                                if str(event.chat_id).startswith("-100") else "لا يوجد رابط")

                    text = f"""#التــاكــات

⌔┊الكــروب : {chat.title}

⌔┊المـرسـل : {sender_name}

⌔┊الرسـالـة : {event.text or '[وسائط]'}

⌔┊رابـط الرسـالة : [link]({msg_link})
"""
                    if "storage_chat_id" in groups:
                        await client.send_message(groups["storage_chat_id"], text, link_preview=False)

            except Exception as e:
                print(f"⌔┊ صار خطأ غير متوقع: {e}")


from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from config import client

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ا(يدي)?$"))
async def user_info(event):
    if not event.out:
        return

    try:
        await event.delete()
    except:
        pass

    replied_msg = await event.get_reply_message()
    if replied_msg:
        user = await replied_msg.get_sender()
        chat_id = replied_msg.chat_id
        reply_to_id = replied_msg.id
    else:
        user = await event.get_sender()
        chat_id = event.chat_id
        reply_to_id = None

    full = await client(GetFullUserRequest(user.id))

    # عدد الصور بالكامل باستخدام len()
    photos_data = await client(GetUserPhotosRequest(
        user_id=user.id,
        offset=0,
        max_id=0,
        limit=0
    ))
    photos_count = len(photos_data.photos)

    first_name = user.first_name or "لا يوجد"
    username = f"@{user.username}" if user.username else "لا يوجد"
    user_id = user.id
    rank = "مـالك الحساب" if user.is_self else "مستخدم"
    bio = getattr(full.full_user, 'about', None) or "لا يوجد"

    caption = f"""•⎚• مـعلومـات المسـتخـدم مـن بـوت 𝐙

ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆
✦ الاســم  ⤎ {first_name}
✦ اليـوزر  ⤎ {username}
✦ الايـدي  ⤎ {user_id}
✦ الرتبــه  ⤎ {rank}
✦ الصـور  ⤎ {photos_count}
✦ البايـو  ⤎ {bio}
ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆"""

    try:
        if photos_count > 0:
            last_photo = await client.get_profile_photos(user.id, limit=1)
            if last_photo.total > 0:
                await client.send_file(
                    chat_id,
                    last_photo[0],
                    caption=caption,
                    reply_to=reply_to_id
                )
                return

        await client.send_message(chat_id, caption, reply_to=reply_to_id)

    except Exception as e:
        print("فشل إرسال الكليشة:", e)


# ------------- أمر انتحال الحساب -------------
import os
from telethon import events, functions
from telethon.tl.functions.users import GetFullUserRequest

original_info = {}

# --------- أمر انتحال حساب ---------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.انتحال$'))
async def impersonate_user(event):
    if not event.out:
        return  # تنفيذ فقط على رسائلك الصادرة

    global original_info

    # التأكد من الرد على رسالة الشخص المراد انتحال حسابه
    user_msg = await event.get_reply_message()
    if not user_msg:
        await event.edit("خـطأ: يـجـب الـرد علـى رسـالة الـشـخص")
        return

    sender = await user_msg.get_sender()

    # حفظ معلومات الحساب الأصلي
    me = await client.get_me()
    profile_photos = await client.get_profile_photos('me')
    original_info['first_name'] = me.first_name or ""
    original_info['last_name'] = me.last_name or ""

    try:
        full_me = await client(GetFullUserRequest(me.id))
        original_info['bio'] = getattr(full_me.full_user, 'about', '')[:70]
    except:
        original_info['bio'] = ""

    original_info['photo'] = None
    if profile_photos.total > 0:
        try:
            file = await client.download_media(profile_photos[0])
            original_info['photo'] = file
        except:
            pass

    # جلب معلومات الشخص المُراد انتحاله
    full_user = await client(GetFullUserRequest(sender.id))
    new_first = sender.first_name or ""
    new_last = sender.last_name or ""
    new_bio = getattr(full_user.full_user, 'about', '')[:70]

    await client(functions.account.UpdateProfileRequest(
        first_name=new_first,
        last_name=new_last,
        about=new_bio
    ))

    photos = await client.get_profile_photos(sender.id, limit=1)
    if photos:
        try:
            file = await client.download_media(photos[0])
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file(file)
            ))
            os.remove(file)
        except:
            pass

    await event.edit("تـم انتـحال الحـسـاب بنـجـاح")

# --------- أمر إعادة الشكل الأصلي ---------
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اعادة$'))
async def restore_original(event):
    if not event.out:
        return  # تنفيذ فقط على رسائلك الصادرة

    global original_info

    if not original_info:
        await event.edit("فـشل إعـادة الحـسـاب إلـى شـكله السـابق")
        return

    await client(functions.account.UpdateProfileRequest(
        first_name=original_info['first_name'],
        last_name=original_info['last_name'],
        about=original_info['bio']
    ))

    if original_info.get('photo'):
        try:
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file(original_info['photo'])
            ))
            os.remove(original_info['photo'])
        except:
            pass

    original_info.clear()
    await event.edit("تـمت إعـادة الحـسـاب إلـى شـكله السـابق")

# ------------- أمر عد الرسائل -------------
from telethon import events

# --- عد الرسائل الصادرة منك ---
@client.on(events.NewMessage(outgoing=True, pattern=r"\.رسائلي$"))
async def my_messages(event):
    if not event.out:
        return  # فقط الصادر منك

    me = await client.get_me()
    count = 0
    async for message in client.iter_messages(event.chat_id, from_user=me.id):
        count += 1

    await event.edit(f"عـدد رسـائلك فـي هـذه المُـحـادثة: {count}")

# --- عد رسائل الشخص الآخر (في المجموعات) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"\.رسائله$"))
async def his_messages(event):
    if not event.out:
        return  # فقط الصادر منك

    if event.is_group or event.is_channel:
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            user_id = reply_msg.sender_id

            count = 0
            async for msg in client.iter_messages(event.chat_id, from_user=user_id):
                count += 1

            user = await client.get_entity(user_id)
            name = user.first_name or "المستخدم"

            await event.edit(f"عـدد رسائل {name} فـي هـذه المُـحـادثة: {count}")
        else:
            await event.edit("❗ يـجـب الـرد على رسـالـة الـشـخص")
    else:
        await event.edit("❗ هـذا الأمـر يعـمل فقـط فـي المـجمـوعـات")

# ------------- أمر فحص البوت -------------
import os
import json
import time
import datetime
import platform
from telethon import events

start_time = datetime.datetime.now()

# مسارات الملفات
FOLDER = "data"
os.makedirs(FOLDER, exist_ok=True)
FILE_PATH = os.path.join(FOLDER, "f7.json")

# تحميل بيانات الفحص
f7_data = {}
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as f:
        f7_data = json.load(f)

def save_f7():
    with open(FILE_PATH, "w") as f:
        json.dump(f7_data, f)

# --- أمر الفحص ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.فحص$'))
async def ping(event):
    me = await client.get_me()
    if not event.out:
        return  # فقط الصادر منك

    try:
        await event.delete()
    except:
        pass

    start = time.perf_counter()
    temp = await event.respond("انتظر .")
    end = time.perf_counter()
    ping_time = round((end - start) * 1000)

    full_name = f"[{me.first_name}](tg://user?id={me.id})"
    pyver = platform.python_version()
    uptime = datetime.datetime.now() - start_time
    uptime_str = str(uptime).split('.')[0]

    await temp.delete()

    user_id = str(me.id)
    data = f7_data.get(user_id, {})
    message_template = data.get("text", (
        "┏━━━━━━━━━━━━━━━┓\n"
        "┃ ✦ 𝙿𝚈𝚃𝙷𝙾𝙽 𝚅𝙴𝚁 : `{pyver}`\n"
        "┃ ✦ 𝙸𝙳 : `{me.id}`\n"
        "┃ ✦ 𝚄𝙿𝚃𝙸𝙼𝙴 : `{uptime_str}`\n"
        "┃ ✦ 𝙽𝙰𝙼𝙴 : {full_name}\n"
        "┗━━━━━━━━━━━━━━━┛\n"
        "┏━━━━━━━━━━━━━━━┓\n"
        "┃ ✦ 𝙿𝙸𝙽𝙶 : `{ping_time}ms`\n"
        "┗━━━━━━━━━━━━━━━┛"
    ))

    try:
        message = message_template.format(
            ping_time=ping_time,
            pyver=pyver,
            uptime_str=uptime_str,
            me=me,
            full_name=full_name
        )
    except Exception as e:
        return await event.reply(f"❌ خطأ في الكليشة:\n{e}")

    image_path = data.get("image")
    if image_path and os.path.exists(image_path):
        await client.send_file(event.chat_id, image_path, caption=message, parse_mode='md')
    else:
        await event.respond(message, parse_mode='md')


# --- تعيين كليشة الفحص ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعيين كليشة الفحص$'))
async def set_f7_text(event):
    if not event.out:
        return  # فقط الصادر منك

    user_id = str((await client.get_me()).id)
    reply = await event.get_reply_message()
    if not reply or not reply.message:
        return await event.edit("❗يـجـب الـرد علـى رسـالة تـحـتوي كليـشة الفـحـص")

    if user_id not in f7_data:
        f7_data[user_id] = {}

    f7_data[user_id]["text"] = reply.message
    save_f7()
    await event.edit("تـم تعـيين كليـشة الفـحـص")


# --- تعيين صورة الفحص ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تعيين صورة الفحص$'))
async def set_f7_image(event):
    if not event.out:
        return  # فقط الصادر منك

    user_id = str((await client.get_me()).id)
    reply = await event.get_reply_message()
    if not reply or not reply.photo:
        return await event.edit("❗ يـجـب الـرد علـى صـورة لتعـييـنها للفـحـص")

    path = await reply.download_media(file=os.path.join(FOLDER, f"f7_{user_id}.jpg"))
    if user_id not in f7_data:
        f7_data[user_id] = {}

    f7_data[user_id]["image"] = path
    save_f7()
    await event.edit("تـم تعـيين صـورة الفـحـص")


# --- حذف كليشة الفحص ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.حذف كليشة الفحص$'))
async def delete_f7_text(event):
    if not event.out:
        return  # فقط الصادر منك

    user_id = str((await client.get_me()).id)
    if user_id in f7_data and "text" in f7_data[user_id]:
        del f7_data[user_id]["text"]
        if not f7_data[user_id]:
            del f7_data[user_id]
        save_f7()
        await event.edit("تـم حـذف كليـشة الفـحـص")
    else:
        await event.edit("❗ لا تـوجـد كليـشة فـحـص محـفوظـة")


# --- حذف صورة الفحص ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.حذف صورة الفحص$'))
async def delete_f7_image(event):
    if not event.out:
        return  # فقط الصادر منك

    user_id = str((await client.get_me()).id)
    if user_id in f7_data and "image" in f7_data[user_id]:
        img = f7_data[user_id]["image"]
        if img and os.path.exists(img):
            os.remove(img)
        del f7_data[user_id]["image"]
        if not f7_data[user_id]:
            del f7_data[user_id]
        save_f7()
        await event.edit("تـم حـذف صـورة الفـحـص")
    else:
        await event.edit("❗ لا تـوجـد صـورة فـحـص محـفوظـة")