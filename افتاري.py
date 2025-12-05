from telethon import events
from config import client   # أخذ الكلاينت من ملف الكونفك

@client.on(events.NewMessage(pattern=r"^\.افتاري$"))
async def send_avatar(event):
    if not event.out:  # تنفيذ فقط من صاحب الحساب
        return
    
    await event.delete()  # حذف الأمر

    # جلب كل صور الحساب
    photos = await client.get_profile_photos("me")

    if not photos:
        return await event.respond("❗️ما عندك افتار حالياً.")

    avatars_count = len(photos)  # عدد صور الحساب
    last_photo = photos[0]       # آخر صورة حساب

    await client.send_file(
        event.chat_id,
        last_photo,
        caption=f"عدد افتاراتك: {avatars_count}"
    )