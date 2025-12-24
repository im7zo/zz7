import os
from telethon import events
from config import client

td = "tmp"
os.makedirs(td, exist_ok=True)

def get_ext(story):
    media = getattr(story, "media", None)
    if hasattr(media, "document") and media.document:
        for a in media.document.attributes:
            if hasattr(a, "file_name"):
                return os.path.splitext(a.file_name)[1]
        if media.document.mime_type:
            return "." + media.document.mime_type.split("/")[-1]
    return ".jpg"


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ستوري (.+)'))
async def story_cmd(event):
    await event.delete()
    target = event.pattern_match.group(1)

    try:
        entity = await client.get_entity(target)

        stories = []
        async for story in client.iter_stories(entity):
            stories.append(story)

        if not stories:
            await client.send_message(event.chat_id, "❗ لا توجد ستوريات حالية")
            return

        info = await client.send_message(
            event.chat_id,
            f"⌯ تم العثور على {len(stories)} ستوري، جاري الإرسال..."
        )

        for st in stories:
            media = getattr(st.media, 'document', None) or getattr(st.media, 'photo', None)
            if not media:
                continue

            ext = get_ext(st)
            path = os.path.join(td, f"story_{st.id}{ext}")

            await client.download_media(media, file=path)
            await client.send_file(event.chat_id, path)
            os.remove(path)

        await info.delete()

    except Exception as e:
        await client.send_message(event.chat_id, "❌ فشل جلب الستاوريات")
        print("STORY ERROR:", e)
