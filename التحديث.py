from telethon import events
import asyncio
import os
import sys
import shutil
import requests
import zipfile

from config import client

# رابط المستودع
ZIP_URL = "https://github.com/im7zo/zz7/archive/refs/heads/main.zip"

# أسماء الملفات والمجلدات
ZIP_FILE = "source_update.zip"
TEMP_EXTRACTED = "zz7-main"
TARGET_FOLDER = "Z"

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تحديث$'))
async def update_all(event):
    msg = await event.edit(
        "ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝐙 🝢 إعــادة التشغيــل\n"
        "•─────────────────•\n\n"
        "⇜ جـارِ إعـادة تشغيـل بـوت 𝐙 . . .🌐\n\n"
        "%0 ▭▭▭▭▭▭▭▭▭▭"
    )

    try:
        # تحميل التحديث
        r = requests.get(ZIP_URL)
        with open(ZIP_FILE, "wb") as f:
            f.write(r.content)

        # تحديث شريط النسبة
        for i in range(20, 61, 20):
            bar = "▬" * (i // 10) + "▭" * ((100 - i) // 10)
            await msg.edit(
                f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝐙 🝢 إعــادة التشغيــل\n"
                f"•─────────────────•\n\n"
                f"⇜ جـارِ إعـادة تشغيـل بـوت 𝐙 . . .🌐\n\n"
                f"%{i} {bar}"
            )
            await asyncio.sleep(0.5)

        # فك الضغط
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall()

        # حذف مجلد Z القديم
        if os.path.exists(TARGET_FOLDER):
            shutil.rmtree(TARGET_FOLDER)

        # إنشاء مجلد جديد
        os.makedirs(TARGET_FOLDER, exist_ok=True)

        # نسخ الملفات من المستودع
        for item in os.listdir(TEMP_EXTRACTED):
            src = os.path.join(TEMP_EXTRACTED, item)
            dst = os.path.join(TARGET_FOLDER, item)

            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        # تنظيف الملفات المؤقتة
        os.remove(ZIP_FILE)
        shutil.rmtree(TEMP_EXTRACTED)

        # نسبة أخيرة
        for i in range(80, 101, 20):
            bar = "▬" * (i // 10) + "▭" * ((100 - i) // 10)
            await msg.edit(
                f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝐙 🝢 إعــادة التشغيــل\n"
                f"•─────────────────•\n\n"
                f"⇜ جـارِ إعـادة تشغيـــل بـوت 𝐙 . . .🌐\n\n"
                f"%{i} {bar}"
            )
            await asyncio.sleep(0.5)

        await msg.edit(
            "•⎆┊أهـلًا عـزيـزي \n"
            "•⎆┊يتـم الآن إعــادة تشغيـل بـوت 𝐙\n"
            "•⎆┊قـد يستغـرق الأمـــر 2-1 دقائـق ▬▭ ..."
        )

        await asyncio.sleep(1)

        # إعادة تشغيل البوت
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        await msg.edit(f"❌ حدث خطأ أثناء التحديث:\n`{str(e)}`")