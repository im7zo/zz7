import json
import os
from telethon import events
from config import client

SHORTCUTS_FILE = "shortcuts.json"
shortcuts_data = {}
shortcuts_enabled = True

# تحميل الاختصارات من الملف
if os.path.exists(SHORTCUTS_FILE):
    with open(SHORTCUTS_FILE, "r", encoding="utf-8") as f:
        shortcuts_data = json.load(f)

# حفظ التغييرات في الملف
def save_shortcuts():
    with open(SHORTCUTS_FILE, "w", encoding="utf-8") as f:
        json.dump(shortcuts_data, f, ensure_ascii=False, indent=2)

# الحصول على معرف الحساب نفسه
async def get_me_id():
    me = await client.get_me()
    return me.id

# .اختصار + مفتاح ← إضافة اختصار بالرد على رسالة معدلة
@client.on(events.NewMessage(pattern=r"^\.اختصار (.+)$"))
async def add_shortcut(event):
    me_id = await get_me_id()
    if event.sender_id != me_id:
        return

    if not event.is_reply:
        return await event.edit("❗يـجـب الـرد علـى رسـالة لإضـافة اخـتصـار")

    key = event.pattern_match.group(1).strip()
    replied = await event.get_reply_message()

    user_id = str(event.sender_id)
    if user_id not in shortcuts_data:
        shortcuts_data[user_id] = {}

    shortcuts_data[user_id][key] = replied.raw_text
    save_shortcuts()
    await event.edit(f" تـم حـفـظ الاخـتصار `{key}` بنـجاح")

# .اختصاراتي ← عرض الاختصارات
@client.on(events.NewMessage(pattern=r"^\.اختصاراتي$"))
async def list_shortcuts(event):
    me_id = await get_me_id()
    if event.sender_id != me_id:
        return

    user_id = str(event.sender_id)
    if user_id not in shortcuts_data or not shortcuts_data[user_id]:
        return await event.edit("لا تـمتلك اخـتصارات")

    text = "⎉╎قائمـة اختصـاراتـك:\n\n"
    for key in shortcuts_data[user_id]:
        text += f"→ `{key}`\n"
    await event.edit(text)

# .حذف اختصار + مفتاح
@client.on(events.NewMessage(pattern=r"^\.حذف اختصار (.+)$"))
async def delete_shortcut(event):
    me_id = await get_me_id()
    if event.sender_id != me_id:
        return

    key = event.pattern_match.group(1).strip()
    user_id = str(event.sender_id)

    if user_id in shortcuts_data and key in shortcuts_data[user_id]:
        del shortcuts_data[user_id][key]
        save_shortcuts()
        await event.edit(f" تـم حـذف الاخـتـصار `{key}` بنـجـاح")
    else:
        await event.edit("❗ لا يـوجـد اخـتـصار بهـذا الاسـم")

# .حذف اختصاراتي ← حذف جميع الاختصارات للمستخدم
@client.on(events.NewMessage(pattern=r"^\.حذف اختصاراتي$"))
async def delete_all_shortcuts(event):
    me_id = await get_me_id()
    if event.sender_id != me_id:
        return

    user_id = str(event.sender_id)
    if user_id in shortcuts_data:
        shortcuts_data[user_id] = {}
        save_shortcuts()
        await event.edit("تـم حـذف جـميع الاخـتـصارات")
    else:
        await event.edit("لا تـمتلك اخـتصارات")

# .تشغيل / .ايقاف الاختصارات
@client.on(events.NewMessage(pattern=r"^\.?(تشغيل|ايقاف) الاختصارات$"))
async def toggle_shortcuts(event):
    me_id = await get_me_id()
    if event.sender_id != me_id:
        return

    global shortcuts_enabled
    cmd = event.pattern_match.group(1)

    if cmd == "تشغيل":
        shortcuts_enabled = True
        await event.edit("تـم تـفعيل الاخـتـصارات")
    else:
        shortcuts_enabled = False
        await event.edit("تـم تـعطيل الاخـتـصارات")

# تفعيل الاختصارات عند مطابقة الرسالة لنص محفوظ
@client.on(events.NewMessage())
async def handle_shortcuts(event):
    me_id = await get_me_id()
    if event.sender_id != me_id:
        return

    if not shortcuts_enabled or event.text is None:
        return

    user_id = str(event.sender_id)
    msg = event.raw_text.strip()

    if user_id in shortcuts_data and msg in shortcuts_data[user_id]:
        await event.edit(shortcuts_data[user_id][msg])