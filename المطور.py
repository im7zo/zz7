from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from config import client

@client.on(events.NewMessage(pattern=r"^\.المطور$|^\.مطور$"))
async def developer_info(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # حذف رسالة الأمر مباشرة
    try:
        await event.delete()
    except:
        pass

    try:
        # جلب معلومات المطور
        user = await client.get_entity('@cfc_5')
        full = await client(GetFullUserRequest(user.id))

        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد يوزرنيم"
        user_id = 7902529889

        # ⭐ جلب البايو تلقائياً بشكل مضمون
        bio = full.about if hasattr(full, "about") and full.about else "لا يوجد بايو"

        rank = "مــطور الـسورس"

        photos = await client.get_profile_photos(user.id, limit=1)

        caption = (
            "•⎚• مـعلومـات الــمطور مـن بـوت 𝐙\n\n"
            "ٴ⋆─┄─┄─┄── 𝐙 ─┄─┄─┄──⋆\n"
            f"✦ الاســم  ⤎ {name}\n"
            f"✦ اليـوزر  ⤎ {username}\n"
            f"✦ الايـدي  ⤎ {user_id}\n"
            f"✦ الرتبــه  ⤎ {rank}\n"
            f"✦ الصـور  ⤎ {photos.total if photos else 0}\n"
            f"✦ البايـو  ⤎ {bio}\n"
            "ٴ⋆─┄─┄─┄── 𝐙 ─┄─┄─┄──⋆"
        )

        if photos.total > 0:
            await client.send_file(event.chat_id, photos[0], caption=caption)
        else:
            await client.send_message(event.chat_id, caption)

    except Exception as e:
        await client.send_message(event.chat_id, f"❌ حدث خطأ: {e}")