import os
from telethon import events
from telethon.tl.functions.stories import GetAllStoriesRequest
from config import client

td = "tmp"
os.makedirs(td, exist_ok=True)

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
async def stories_cmd(event):
    await event.delete()
    target = event.pattern_match.group(1)

    try:
        entity = await client.get_entity(target)

        res = await client(GetAllStoriesRequest(
            next=False,
            hidden=False,
            state=0
        ))

        user_stories = []
        for peer, stories in res.peer_stories.items():
            if peer == entity:
                user_stories = stories.stories
                break

        if not user_stories:
            await client.send_message(event.chat_id, "❗ لا توجد ستوريات حالية")
            return

        info = await client.send_message(
            event.chat_id,
            f"⌯ تم العثور على {len(user_stories)} ستوري، جاري الإرسال..."
        )

        for st in user_stories:
            media = getattr(st.media, 'document', None) or getattr(st.media, 'photo', None)
            if not media:
                continue

            ext = ge(st)
            path = os.path.join(td, f"story_{st.id}{ext}")

            await client.download_media(media, file=path)
            await client.send_file(event.chat_id, path)
            os.remove(path)

        await info.delete()

    except Exception as e:
        await client.send_message(event.chat_id, "❌ فشل جلب الستوريات")
        print("STORY ERROR:", e)
