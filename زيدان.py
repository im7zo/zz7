from telethon import events
from config import client  # تأكد أن client معرف في ملف config.py أو عدّل الاستيراد حسب سورسك

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.زيدان(?:\s.*)?$'))
async def zidan_edit(event):
    """عند إرسال .زيدان يتم تعديل نفس الرسالة إلى Z"""
    try:
        await event.edit("Z")
    except Exception as e:
        # إظهار خطأ لو صار شيء (اختياري)
        await event.reply(f"❌ خطأ عند تعديل الرسالة:\n{e}")