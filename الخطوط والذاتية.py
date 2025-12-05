from config import client
from telethon import events

active_font = None

# تفعيل / إيقاف الخط
@client.on(events.NewMessage(pattern=r"\.(خط غامق|خط مشطوب|خط رمز|خط بايثون|خط برنت)"))
async def text_styles(event):

    # فقط رسائلك انت
    if not event.out:
        return

    global active_font
    cmd = event.pattern_match.group(1)

    # إيقاف نفس النمط إذا كان مفعل
    if active_font == cmd:
        active_font = None
        return await event.edit(f"تـم ايـقاف `{cmd}`")

    # تفعيل النمط
    active_font = cmd
    await event.edit(f"تـم تفـعـيل `{cmd}`.")


# تطبيق النمط تلقائيًا
@client.on(events.NewMessage())
async def auto_font(event):

    # فقط رسائلك انت
    if not event.out:
        return

    global active_font

    # إذا لا يوجد نمط فعال → تجاهل
    if not active_font:
        return

    text = event.raw_text

    # تجاهل الأوامر اللي تبدأ بنقطة
    if text.startswith("."):
        return

    style = active_font

    if style == "خط غامق":
        styled = f"**{text}**"

    elif style == "خط مشطوب":
        styled = f"~~{text}~~"

    elif style == "خط رمز":
        styled = f"`{text}`"

    elif style == "خط بايثون":
        styled = f"```python\nprint(\'{text}\')\n```"

    elif style == "خط برنت":
        styled = f"```{text}```"

    else:
        return

    # تعديل الرسالة وتطبيق الخط
    await event.edit(styled)



import os
from telethon import events

SAVE_PATH = "temp_self_media"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

save_self_destruct = False  # الحالة التلقائية

# ==========================
# أمر تفعيل/تعطيل الحفظ التلقائي
@client.on(events.NewMessage(outgoing=True, pattern=r"\.حفظ الذاتية"))
async def toggle_auto_save(event):
    global save_self_destruct
    save_self_destruct = not save_self_destruct
    state = "مـفـعل" if save_self_destruct else "مـعـطل"
    await event.edit(f"📮 الـحـفظ التلـقائي للـذاتـية ، {state}")


# ==========================
# أمر يدوي .ذاتية
@client.on(events.NewMessage(outgoing=True, pattern=r"\.ذاتية"))
async def save_self_destruct_once(event):
    # حذف الأمر
    try:
        await event.delete()
    except:
        pass

    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return

    # التأكد أنها وسائط ذاتية التدمير
    if not getattr(reply.media, "ttl_seconds", None):
        return

    try:
        path = await reply.download_media(file=SAVE_PATH)
        sender = await reply.get_sender()
        sender_name = f"[{sender.first_name}](tg://user?id={sender.id})"

        caption = (
            "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 - حفـظ الذاتـيـة  .\n"
            "⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
            "𝑍╎مࢪحبـًا عـزيـزي المـالك\n"
            "𝑍╎ تـم حفـظ الذاتيـة .. بنجـاح  \n"
            f"𝑍╎المرسـل: {sender_name}"
        )

        await client.send_file("me", path, caption=caption, link_preview=False)
        os.remove(path)

    except Exception:
        pass


# ==========================
# الحفظ التلقائي للوسائط المؤقتة (الواردة إليك فقط)
@client.on(events.NewMessage(incoming=True))
async def auto_save_self_destruct(event):
    global save_self_destruct
    if not save_self_destruct:
        return

    if not event.media:
        return

    if not getattr(event.media, "ttl_seconds", None):
        return  # ليست ذاتية التدمير

    try:
        path = await event.download_media(file=SAVE_PATH)
        sender = await event.get_sender()
        sender_name = f"[{sender.first_name}](tg://user?id={sender.id})"

        caption = (
            "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 - حفـظ الذاتـيـة  .\n"
            "⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
            "𝑍╎مࢪحبـًا عـزيـزي المـالك\n"
            "𝑍╎ تـم حفـظ الذاتيـة تلقائيـًا .. بنجـاح  \n"
            f"𝑍╎المرسـل: {sender_name}"
        )

        await client.send_file("me", path, caption=caption, link_preview=False)
        os.remove(path)

    except Exception as e:
        print(f"❌ فشل الحفظ التلقائي: {e}")

        # قنوات المستخدم
@client .on (events .NewMessage (pattern =r"\.قائمة قنواتي"))
async def list_my_channels (event ):
    result =""
    async for dialog in client .iter_dialogs ():
        entity =dialog .entity 
        if getattr (entity ,"broadcast",False )and getattr (entity ,"creator",False ):
            result +=f"• {dialog.name}\n"
    await event .edit (result or "❌ لا توجد قنوات تملكها.")

    # كروبات أنت مشرف بها
@client .on (events .NewMessage (pattern =r"\.قائمة كروباتي"))
async def list_my_groups (event ):
    result =""
    async for dialog in client .iter_dialogs ():
        if dialog .is_group and dialog .entity .admin_rights :
            result +=f"• {dialog.name}\n"
    await event .edit (result or "❌ لا توجد مجموعات أنت مشرف بها.")