import os
import pickle
from telethon import events, functions
from config import client  # client معرف مسبقًا

# ================== التأكد من وجود مجلد data ==================
if not os.path.exists("data"):
    os.makedirs("data")

watchlist_file = "data/watchlist.pkl"
user_data_file = "data/user_data.pkl"
monitoring_channel_file = "data/monitoring_channel.pkl"

watchlist = {}
user_data = {}
monitoring_channel = None

# ================== تحميل البيانات المحفوظة ==================
if os.path.exists(watchlist_file):
    with open(watchlist_file, "rb") as f:
        watchlist = pickle.load(f)

if os.path.exists(user_data_file):
    with open(user_data_file, "rb") as f:
        user_data = pickle.load(f)

if os.path.exists(monitoring_channel_file):
    with open(monitoring_channel_file, "rb") as f:
        monitoring_channel = pickle.load(f)

# ================== دوال الحفظ ==================
def save_watchlist():
    with open(watchlist_file, "wb") as f:
        pickle.dump(watchlist, f)

def save_user_data():
    with open(user_data_file, "wb") as f:
        pickle.dump(user_data, f)

def save_monitoring_channel():
    with open(monitoring_channel_file, "wb") as f:
        pickle.dump(monitoring_channel, f)

# ================== التأكد من وجود قناة المراقبة ==================
async def ensure_monitoring_channel():
    global monitoring_channel
    if monitoring_channel:
        return monitoring_channel
    try:
        result = await client(functions.channels.CreateChannelRequest(
            title="قـناة الــمـراقـبة",
            about="@imzl7",
            megagroup=False
        ))
        monitoring_channel = result.chats[0].id
        save_monitoring_channel()
        print(f"⌔┊ تم إنشاء القناة: {monitoring_channel}")
    except Exception as e:
        print(f"⌔┊ فشل إنشاء القناة: {e}")
        monitoring_channel = None
    return monitoring_channel

# ================== بدء المراقبة ==================
@client.on(events.NewMessage(pattern=r"\.مراقبة (.+)"))
async def start_watching(event):
    if not event.out:
        return
    username = event.pattern_match.group(1)
    channel_id = await ensure_monitoring_channel()
    if channel_id is None:
        await event.edit("❗فشـل فـي انـشـاء القـناة حـاول لاحـقا")
        return
    try:
        user = await client.get_entity(username)
        if user.id in watchlist:
            await event.edit(f"المـستـخـدم @{watchlist[user.id]} قيـد المـراقبـة بالفـعل")
            return
        
        # حفظ بيانات الحساب للمراقبة
        watchlist[user.id] = user.username or user.first_name
        user_data[user.id] = {
            'name': user.first_name,
            'photo': None,
            'bio': None
        }
        save_watchlist()
        save_user_data()

        # الحصول على الصورة الأولى
        photos = await client.get_profile_photos(user.id, limit=1)

        # الحصول على البايو
        full_user = await client(functions.users.GetFullUserRequest(user))
        bio = getattr(full_user.full_user, 'about', None)
        if bio:
            user_data[user.id]['bio'] = bio
            save_user_data()

        # إرسال البيانات الأولية للقناة
        msg_text = f"⌔┊ بدأت مراقبة المستخدم @{watchlist[user.id]}:\n\n"
        msg_text += f"✦ الاســم → : {user.first_name}\n"
        if user.username:
            msg_text += f"✦ اليـوزر → : @{user.username}\n"
        if bio:
            msg_text += f"✦ البايـو  →: {bio}\n"

        if photos:
            await client.send_file(
                monitoring_channel,
                photos[0],
                caption=msg_text,
                force_document=False
            )
        else:
            await client.send_message(monitoring_channel, msg_text)

        await event.edit(f"بـدأت مراقـبة المُسـتخـدم @{watchlist[user.id]} ")
    except Exception as e:
        await event.edit(f"❗ لـم يتـم العـثـور عـلى المسـتخـدم {username}")
        print(f"Error: {e}")

# ================== إيقاف المراقبة ==================
@client.on(events.NewMessage(pattern=r"\.ايقاف_المراقبة (.+)"))
async def stop_watching(event):
    if not event.out:
        return
    username = event.pattern_match.group(1)
    try:
        user = await client.get_entity(username)
        if user.id in watchlist:
            del watchlist[user.id]
            del user_data[user.id]
            save_watchlist()
            save_user_data()
            await event.edit(f"❗تـم إيقـاف مراقـبة المـستخـدم @{username}")
        else:
            await event.edit(f"❗المـستخـدم @{username} غيـر موجـود فـي قائـمـة المـراقـبة")
    except Exception as e:
        await event.edit(f"❗لـم يـتم العثـور علـى المسـتخـدم {username}")
        print(f"Error: {e}")

# ================== متابعة التغييرات ==================
@client.on(events.UserUpdate)
async def user_update_handler(event):
    global monitoring_channel
    if not monitoring_channel:
        return
    user_id = event.user_id
    if user_id in watchlist:
        try:
            user = await client.get_entity(user_id)
            old_data = user_data.get(user_id, {})
            changes = []

            # الاسم
            if user.first_name != old_data.get('name'):
                changes.append(f"الاسـم الجـديـد: {user.first_name}")
                user_data[user_id]['name'] = user.first_name

            # اليوزر
            if user.username and user.username != watchlist[user_id]:
                changes.append(f"اليـوزر الجـديـد: @{user.username}")
                watchlist[user_id] = user.username

            # الصورة
            photos = await client.get_profile_photos(user_id, limit=1)
            if photos:
                new_photo_id = photos[0].id
                if new_photo_id != old_data.get('photo'):
                    user_data[user_id]['photo'] = new_photo_id
                    user_mention = f"@{watchlist[user_id]}" if watchlist[user_id].startswith("@") else watchlist[user_id]
                    await client.send_file(
                        monitoring_channel,
                        photos[0],
                        caption=f"{user_mention} غـير افـتاره",
                        force_document=False
                    )

            # البايو
            full_user = await client(functions.users.GetFullUserRequest(user))
            bio = getattr(full_user.full_user, 'about', None)
            if bio and bio != old_data.get('bio'):
                changes.append(f"قـام بتـغييـر البـايـو: {bio}")
                user_data[user_id]['bio'] = bio

            save_user_data()
            save_watchlist()

            # إرسال التغييرات الأخرى
            if changes:
                user_mention = f"@{watchlist[user_id]}" if watchlist[user_id].startswith("@") else user.first_name
                await client.send_message(
                    monitoring_channel,
                    f"تحـديث فـي حسـاب {user_mention}:\n\n" + "\n".join(changes)
                )
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")