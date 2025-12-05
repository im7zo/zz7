import asyncio
from telethon import events
from config import client

# ----------------- سحب كل الرسائل -----------------
@client.on(events.NewMessage(outgoing=True, pattern=r"\.سحب كامل المحتوى (@\w+)"))
async def fetch_all_messages(event):
    channel = event.pattern_match.group(1)
    dest_chat = event.chat_id
    await event.edit("جـار حـساب عـدد الرسـائل")

    try:
        total = 0
        success = 0
        failed = 0

        # إرسال تقرير مبدأي
        await client.send_message(dest_chat, f"""جاري سحب المحتوى انتظر
ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆
• إجمالي الرسائل ← سيتم سحب كامل المحتوى 📩
• تم سحب ← جاري الحساب ✔️
• تم تخطي ← جاري الحساب ❗
• نسبة النجاح ← جاري الحساب 😜""")

        async for msg in client.iter_messages(channel, reverse=True):
            total += 1
            try:
                if msg.media:
                    await client.send_file(dest_chat, msg)
                else:
                    await client.send_message(dest_chat, msg.text)
                success += 1
                await asyncio.sleep(0.3)
            except:
                failed += 1

        percentage = round((success / total) * 100, 2) if total else 0
        await client.send_message(dest_chat, f"""تـم سحب كامـل المـحـتوى
ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆
• إجمالي الرسائل ← {total} 📩
• تم سحب ← {success} ✔️
• تم تخطي ← {failed} ❗
• نسبة النجاح ← {percentage}٪ 😜""")

    except Exception as e:
        await event.respond(f"حدث خطأ: {e}")


# ----------------- سحب نطاق محدد -----------------
@client.on(events.NewMessage(outgoing=True, pattern=r"\.سحب من الى (@\w+)\s+(\d+)\s*-\s*(\d+)"))
async def fetch_range_messages(event):
    channel = event.pattern_match.group(1)
    min_id = int(event.pattern_match.group(2))
    max_id = int(event.pattern_match.group(3))
    dest_chat = event.chat_id

    if min_id > max_id:
        min_id, max_id = max_id, min_id

    total = max_id - min_id + 1
    success = 0
    failed = 0

    await client.send_message(dest_chat, f"""جاري سحب المحتوى انتظر
ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆
• إجمالي الرسائل ← {total} 📩
• تم سحب ← جاري الحساب ✔️
• تم تخطي ← جاري الحساب ❗
• نسبة النجاح ← جاري الحساب 😜""")

    for msg_id in range(min_id, max_id + 1):
        try:
            msg = await client.get_messages(channel, ids=msg_id)
            if msg:
                if msg.media:
                    await client.send_file(dest_chat, msg)
                else:
                    await client.send_message(dest_chat, msg.text)
                success += 1
                await asyncio.sleep(0.3)
        except:
            failed += 1

    percentage = round((success / total) * 100, 2) if total else 0
    await client.send_message(dest_chat, f"""تم السحب من {min_id} إلى {max_id}
ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆
• إجمالي الرسائل ← {total} 📩
• تم سحب ← {success} ✔️
• تم تخطي ← {failed} ❗
• نسبة النجاح ← {percentage}٪ 😜""")