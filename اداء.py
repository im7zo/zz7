from telethon import events
from telethon.tl.types import MessageEntityCustomEmoji
from config import client
import time, platform, os, json, re

START_TIME = time.time()
F8_FILE = "f8.json"

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
    text = reply.text or ""

    entities = []
    for e in (reply.entities or []):
        if isinstance(e, MessageEntityCustomEmoji):
            entities.append({
                "offset": e.offset,
                "length": e.length,
                "document_id": e.document_id
            })

    with open(F8_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "text": text,
            "entities": entities
        }, f, ensure_ascii=False, indent=2)

    await event.edit(
        f"تـم تعيـين كليـشـة الأداء بنـجـاح \n"
        f"عـدد الإيمــوجـي المـخصـص {len(entities)}"
    )

# ────────────────
# أمر الأداء
# ────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"\.(اداء|الاداء)$"))
async def performance(event):
    if not os.path.exists(F8_FILE):
        return await event.edit("لـم يـتم تـعيين كـليشة الاداء .")

    try:
        await event.delete()
    except:
        pass

    # ── قياس البنغ الحقيقي ──
    start = time.perf_counter()
    wait = await event.respond("انتظر ...")
    end = time.perf_counter()
    ping_time = f"{round((end - start) * 1000)}ms"
    await wait.delete()

    me = await client.get_me()
    full_name = me.first_name or ""
    if me.last_name:
        full_name += f" {me.last_name}"

    variables = {
        "pyver": platform.python_version(),
        "uptime_str": format_uptime(int(time.time() - START_TIME)),
        "full_name": full_name,
        "ping_time": ping_time
    }

    with open(F8_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_text = data["text"]

    # ── نحسب فروقات الطول لكل متغير ──
    shifts = []
    for match in re.finditer(r"\{(\w+)\}", raw_text):
        key = match.group(1)
        if key in variables:
            old_len = len(match.group(0))
            new_len = len(variables[key])
            diff = new_len - old_len
            shifts.append((match.start(), diff))

    # ── نحاول تنسيق النص مع حماية ──
    try:
        text = raw_text.format(**variables)
    except Exception:
        text = raw_text

    # ── إضافة Zero-Width Space بين الإيموجيات المكررة لتظهر كلها مميزة ──
    def fix_emoji_spacing(txt, entities):
        new_txt = list(txt)
        new_entities = []
        added = 0

        for e in entities:
            offset = e["offset"] + added
            length = e["length"]

            # إذا الإيموجي مكرر، نضيف \u200b بين كل واحد
            emoji_text = txt[offset:offset+length]
            if len(emoji_text) > 1:
                spaced = "\u200b".join(emoji_text)
                new_txt[offset:offset+length] = list(spaced)
                length = len(spaced)
                added += length - (e["length"])

            new_entities.append(
                MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=e["document_id"]
                )
            )
        return "".join(new_txt), new_entities

    text, fixed_entities = fix_emoji_spacing(text, data["entities"])

    # ── إرسال الكليشة مع الإيموجي المميز ──
    await client.send_message(
        event.chat_id,
        text,
        formatting_entities=fixed_entities
    )
