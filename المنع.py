import json
import os
from telethon import events
from config import client

# التأكد من وجود مجلد data
if not os.path.exists("data"):
    os.makedirs("data")

BLOCK_FILE = "data/blocked_words.json"

# تحميل الكلمات المحظورة
def load_blocked():
    try:
        with open(BLOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# حفظ الكلمات المحظورة
def save_blocked(data):
    with open(BLOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# أمر منع كلمة (فقط من صاحب الحساب)
@client.on(events.NewMessage(pattern=r"^\.منع كلمة (.+)"))
async def block_word(event):
    if not event.out:  # الرسائل الصادرة من حسابك فقط
        return

    word = event.pattern_match.group(1).strip()
    chat_id = str(event.chat_id)

    blocked = load_blocked()
    if chat_id not in blocked:
        blocked[chat_id] = []

    if word in blocked[chat_id]:
        return await event.edit(f"❗تـم مـنع الكلـمة مـسبقًـا (`{word}`)")

    blocked[chat_id].append(word)
    save_blocked(blocked)
    await event.edit(f"تـم مـنـع الكـلمـة (`{word}`)")

# أمر حذف كلمة من المنع (فقط من صاحب الحساب)
@client.on(events.NewMessage(pattern=r"^\.حذف كلمة المنع (.+)"))
async def unblock_word(event):
    if not event.out:
        return

    word = event.pattern_match.group(1).strip()
    chat_id = str(event.chat_id)

    blocked = load_blocked()
    if chat_id in blocked and word in blocked[chat_id]:
        blocked[chat_id].remove(word)
        save_blocked(blocked)
        await event.edit(f"تـم حـذف كـلمة المـنع (`{word}`)")
    else:
        await event.edit("❗هـذهِ الكـلمة غيـر موجـودة فـي كلـمات المـنع")

# أمر عرض قائمة الكلمات (فقط من صاحب الحساب)
@client.on(events.NewMessage(pattern=r"^\.قائمة المنع$"))
async def list_blocked_words(event):
    if not event.out:
        return

    chat_id = str(event.chat_id)
    blocked = load_blocked()

    if chat_id not in blocked or not blocked[chat_id]:
        return await event.edit("❗لا تـوجد كلـمات ممنـوعة فـي هـذا الكـروب")

    words = "\n".join([f"• `{word}`" for word in blocked[chat_id]])
    await event.edit(f"⌯ قائمة الكلمات الممنوعة:\n{words}")

# مراقبة الرسائل للكلمات المحظورة وحذفها مع تنبيه
@client.on(events.NewMessage())
async def monitor_blocked_words(event):
    if not event.is_group:
        return

    chat_id = str(event.chat_id)
    blocked = load_blocked()

    if chat_id in blocked:
        for word in blocked[chat_id]:
            if word in event.raw_text:
                user = await event.get_sender()
                username = user.username if user.username else str(user.id)

                # حذف رسالة المستخدم الذي كتب الكلمة
                try:
                    await event.delete()
                except:
                    pass

                # إرسال رسالة تنبيهية
                await event.respond(
                    f"⌯ | لقد تم منع هذهِ الكلمة هنا\n⌯ | ازحلك عزيزي @{username}"
                )
                break