from telethon import events
from config import client

OWNER_ID = 7902529889  # آيديك، للتأكد من المطور

@client.on(events.NewMessage(outgoing=True, pattern=r"\.رفع مرتي(?:\s|$)([\s\S]*)"))
async def raise_wife(event):

    # الحصول على الرسالة المردودة
    reply = await event.get_reply_message()
    if not reply:
        await event.edit("** يجب الرد على رسالة الشخص الذي تريد رفعه!**")
        return

    user = reply.sender
    if not user:
        await event.edit("** لم أتمكن من الحصول على بيانات المستخدم.**")
        return

    # إذا كان المطور نفسه
    if user.id == OWNER_ID:
        await event.edit("**-امـشـي لك مـطـور السورس هذا  **")
        return

    # اسم المستخدم أو الاسم الأخير
    mahd = (user.last_name.replace("\u2060", "") if user.last_name else (user.username or "لا يوجد اسم"))

    # بياناتك انت
    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    # إرسال رسالة النجاح
    cliche = f"""🚻 **⎙︙ المستخدم => •** [{mahd}](tg://user?id={user.id})
☑️ **⎙︙ تم رفعها مرتك بواسطة :** {my_mention} 👰🏼‍♀️
"""
    await event.edit(cliche)