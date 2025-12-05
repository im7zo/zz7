from telethon import events
from config import client  # استيراد الكلاينت من ملف config

# القناة التي تحتوي على الملفات
channel_username = "@zzio5"

# ربط الأمر برقم الرسالة للقناة
python_files = {
    ".ملف سورس نشر تلقائي": 706,
    ".ملف بوت تحويل الصوت الى كلام": 707,
    ".بوت سايت": 708,
    ".بوت xo": 709,
    ".ملف سورس انشاء القروبات بالحسـاب": 710,
    ".اداة صيد يوزرات تلي": 711,
    ".ملف بوت حفظ من القنوات المقيدة": 712,
    ".ملف بوت تيك": 713,
    ".ملف بوت تواصل": 714,
    ".ملف بوت يوت": 715
}

# رسالة المكتبة
library_message = """
⋆─┄─┄─┄─ الـملـفـات ─┄─┄─┄─⋆

`.ملف سورس نشر تلقائي`
`.ملف بوت تحويل الصوت الى كلام`
`.ملف سورس انشاء القروبات بالحسـاب`
`.اداة صيد يوزرات تلي`
`.ملف بوت حفظ من القنوات المقيدة`
`.ملف بوت تيك`
`.ملف بوت تواصل`
`.ملف بوت يوت`
`.بوت سايت`
`.بوت xo`
"""

# عرض المكتبة
@client.on(events.NewMessage(outgoing=True, pattern=r"\.بايثون$"))
async def library_intro(event):
    await event.edit(library_message)


# ===== إرسال ملف بايثون حسب الأمر =====
@client.on(events.NewMessage(outgoing=True, pattern=r"\.(.+)$"))
async def send_python_file(event):
    cmd = event.raw_text.strip()

    # تجاهل أمر .بايثون لأنه مخصص لعرض المكتبة
    if cmd == ".بايثون":
        return

    msg_id = python_files.get(cmd)
    if not msg_id:
        return  # تجاهل الأوامر الغير موجودة

    try:
        msg = await client.get_messages(channel_username, ids=msg_id)
        if msg and msg.document and msg.file.name.endswith(".py"):
            caption = msg.text or f"هـذا هـو المـلف `{msg.file.name}`"
            await client.send_file(event.chat_id, msg.document, caption=caption)
        else:
            await event.edit("❗ الـمـلف غيـر مـوجـود ")
    except Exception as e:
        await event.edit(f"حـدث خـطأ أثنـاء جـلب المـلف: {e}")