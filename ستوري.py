import os
import re
from telethon import events
from telethon.tl.functions.stories import GetStoriesByIDRequest
from config import client

td = "tmp"
os.makedirs(td, exist_ok=True)

# استخراج اسم المستخدم وID الستوري من الرابط
def px(u):
    m = re.search(r't\.me/([^/?]+)/(?:s/|\?story=)?(\d+)', u)
    if m:
        return m.group(1), int(m.group(2))
    return None, None

# تحديد امتداد الملف
def ge(st):
    d = getattr(st.media, 'document', None)
    if d:
        for a in d.attributes:
            if hasattr(a, 'file_name'):
                ext = os.path.splitext(a.file_name)[1]
                if ext:
                    return ext
        if d.mime_type:
            return '.' + d.mime_type.split('/')[-1]
    return '.bin'

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تحميل (.+)'))
async def dl(e):
    await e.delete()  # حذف أمر .تحميل

    lnk = e.pattern_match.group(1)
    us, sid = px(lnk)

    if not us or not sid:
        await e.respond("الـرابط غـير صـحـيح")
        return

    try:
        en = await client.get_entity(us)
        rs = await client(GetStoriesByIDRequest(peer=en, id=[sid]))

        if not rs.stories:
            await e.respond("❗لـم يـتم العـثور علـى السـتـوري")
            return

        st = rs.stories[0]
        md = getattr(st.media, 'document', None) or getattr(st.media, 'photo', None)

        if not md:
            await e.respond("❗الـستـوري بـدون وسـائط")
            return

        ex = ge(st)
        fp = os.path.join(td, f"st{sid}{ex}")

        # إنشاء رسالة تقدم مبدئية
        progress_msg = await e.respond("⌯ جاري التحميل: 0%")
        last_percent = 0

        async def update_progress(received, total):
            nonlocal last_percent
            if total:
                percent = int((received / total) * 100)
                if percent != last_percent:
                    last_percent = percent
                    try:
                        await progress_msg.edit(f"⌯ جاري التحميل: {percent}%")
                    except:
                        pass

        path = await client.download_media(md, file=fp, progress_callback=update_progress)

        if not path or not os.path.isfile(path):
            await progress_msg.edit("فـشل التـحميـل")
            return

        await client.send_file(e.chat_id, path)
        os.remove(path)

        # حذف رسالة التقدم بعد الإرسال
        await progress_msg.delete()

    except Exception as er:
        await e.respond("صـار خـطأ أثنـاء التـحمـيل")
        print("Err:", er)