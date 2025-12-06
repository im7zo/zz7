from telethon import events
from config import client
import requests
import os

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.سكرين (.+)$'))
async def link_scan(event):
    url = event.pattern_match.group(1).strip()

    # تصحيح الرابط
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    await event.edit("جارِ التقاط صورة للموقع ...")

    try:
        # رابط API الخاص بصورة الموقع
        screenshot_url = f"https://image.thum.io/get/fullpage/{url}"

        # تنزيل الصورة
        img_data = requests.get(screenshot_url).content
        file_path = "z.jpg"
        with open(file_path, "wb") as f:
            f.write(img_data)

        # إرسال الصورة كملف وليس كمعاينة
        await client.send_file(
            event.chat_id,
            file_path,
            caption=f"تـم التـقاط صـورة للمـوقع بنـجاح ✔️",
            force_document=True
        )
        await event.delete()

        # حذف الصورة من التخزين المحلي
        os.remove(file_path)

    except Exception as e:
        await event.edit(f"❗حـدث خـطأ أثنـاء التقاط صورة للموقع \n{e}")