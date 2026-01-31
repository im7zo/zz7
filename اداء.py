from telethon import events
from telethon.tl.types import MessageEntityCustomEmoji
from config import client
import time, platform, os, json

START_TIME = time.time()
F8_FILE = "f8.json"  # ملف حفظ الكليشة

def format_uptime(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}h {m}m {s}s"

# ────────────────
# تعيين كليشة الأداء
# ────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"\.تعيين كليشة الاداء$"))
async def set_performance(event):
    if not event.is_reply:
        return await event.edit("❗يـجـب الـرد علـى رسـالة تـحـتوي كليـشة الاداء .")

    reply = await event.get_reply_message()
    text = reply.text
    entities = []
    for e in (reply.entities or []):
        if isinstance(e, MessageEntityCustomEmoji):
            entities.append({
                "offset": e.offset,
                "length": e.length,
                "document_id": e.document_id
            })
    media = getattr(reply, "media", None)

    # حفظ كل شيء في ملف f8.json
    with open(F8_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "text": text,
            "entities": entities,
            "media": media.to_dict() if media else None  # تخزين بيانات الوسائط
        }, f, ensure_ascii=False, indent=2)

    await event.edit(f"تـم تعيـين كليـشـة الأداء بنـجـاح!\nعـدد الإيمــوجـي المـخصـص {len(entities)}")

# ────────────────
# أمر الأداء
# ────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"\.اداء$"))
async def performance(event):
    if not os.path.exists(F8_FILE):
        return await event.edit("لـم يـتم تـعيين كـليشة الاداء .")

    try:
        await event.delete()
    except:
        pass

    start = time.perf_counter()
    temp = await event.respond("انتظر ...")
    end = time.perf_counter()
    ping_time = round((end - start) * 1000)

    me = await client.get_me()
    full_name = me.first_name or ""
    if me.last_name:
        full_name += f" {me.last_name}"
    pyver = platform.python_version()
    uptime_str = format_uptime(int(time.time() - START_TIME))

    # قراءة الكليشة من الملف
    with open(F8_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    text_template = data["text"]
    text = text_template.format(
        pyver=pyver,
        uptime_str=uptime_str,
        full_name=full_name,
        ping_time=f"{ping_time}ms"
    )

    # تجهيز الإيموجيات المخصصة
    entities = []
    for e in data.get("entities", []):
        entities.append(MessageEntityCustomEmoji(
            offset=e["offset"],
            length=e["length"],
            document_id=e["document_id"]
        ))

    # إرسال الرسالة مع الوسائط والإيموجيات
    media = data.get("media")
    if media:
        await client.send_file(event.chat_id, media, caption=text, formatting_entities=entities)
    else:
        await client.send_message(event.chat_id, text, formatting_entities=entities)
    await temp.delete()