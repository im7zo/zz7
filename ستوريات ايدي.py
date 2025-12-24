import os
from telethon import events
from telethon.tl.functions.stories import GetPeerStoriesRequest
from config import client

td = "tmp"
os.makedirs(td, exist_ok=True)

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
    return '.jpg'


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ستوري (.+)'))
async def get_stories(event):
    await event.delete()

    target = event.pattern_match.group(1)

    try:
        entity = await client.get_entity(target)

        res = await client(GetPeerStoriesRequest(peer=entity))

        if not res.stories or not res.stories.stories:
            await client.send_message(event.chat_id, "❗ لا توجد ستوريات حالية لهذا الحساب")
            return

        msg = await client.send_message(event.chat_id, f"⌯ تم العثور على {len(res.stories.stories)} ستوري، جاري الإرسال...")

        for st in res.stories.stories:
            media = getattr(st.media, 'document', None) or getattr(st.media, 'photo', None)
            if not media:
                continue

            ext = ge(st)
            path = os.path.join(td, f"story_{st.id}{ext}")

            await client.download_media(media, file=path)
            await client.send_file(event.chat_id, path)
            os.remove(path)

        await msg.delete()

    except Exception as e:
        await client.send_message(event.chat_id, "❌ حدث خطأ أثناء جلب الستوريات")
        print("Story Error:", e)