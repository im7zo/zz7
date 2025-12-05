import re
import os
from telethon import events, errors
from config import client 

@client.on(events.NewMessage(pattern=r'^\.مقيد\s+(\S+)$'))
async def save_protected_post(event):

    # السماح فقط لصاحب الحساب
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    link = event.pattern_match.group(1)
    msgx = await event.edit("يـتم حـفظ المـحتوى 📮")

    try:
        link = link.split('?')[0].rstrip('/')

        m_user = re.search(r't\.me/([^/]+)/(\d+)$', link)
        m_c = re.search(r't\.me/c/(\d+)/(\d+)$', link)

        if m_user:
            username = m_user.group(1)
            msg_id = int(m_user.group(2))
            msg = await client.get_messages(username, ids=msg_id)

        elif m_c:
            short_id = m_c.group(1)
            msg_id = int(m_c.group(2))
            chat_id = int(f"-100{short_id}")
            msg = await client.get_messages(chat_id, ids=msg_id)

        else:
            await msgx.edit("- إلـرابط غـير صـحـيح ❌")
            return

        if not msg:
            await msgx.edit("صـار خـلل اثنـاء التـحميل ❌")
            return

        temp_dir = "temp_media"
        os.makedirs(temp_dir, exist_ok=True)

        if msg.media:
            file_path = await msg.download_media(file=temp_dir)
            await client.send_file(event.chat_id, file_path)
            os.remove(file_path)

        else:
            await client.send_message(event.chat_id, msg.message)

        await event.delete()
        await msgx.delete()

    except Exception as e:
        await msgx.edit(f"❌ حدث خطأ: {e}")