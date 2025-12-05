# create_groups.py

import asyncio
from datetime import datetime
from telethon import events, functions
from config import client  # تأكد أن client معرف ومُستورد من ملف الإعدادات الرئيسي
import time

# تحويل الأرقام إلى العربية
def to_arabic_number(n):
    return str(n).translate(str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩"))

# أمر .صنع كروبات
@client.on(events.NewMessage(pattern=r'\.قروب(?: (\d+))?'))
async def create_groups(event):
    # التأكد أن الأمر صادر مني فقط
    me = await client.get_me()
    sender = await event.get_sender()
    if sender.bot or sender.id != me.id:
        return  # تجاهل أي أوامر من الآخرين

    count = int(event.pattern_match.group(1) or 50)
    if count > 50:
        await event.edit("**❗الـحد الأقـصى هـو 50 كـروب فقـط**")
        return 

    

    start_time = time.time()
    today = datetime.now().strftime("%Y/%m/%d")
    group_links = []
    success = 0
    fail = 0

    for i in range(1, count + 1):
        try:
            # إنشاء الكروب
            group_title = f"𝐒𝐎𝐔𝐑𝐂𝐄 𝐙 | {i}# | {today}"
            result = await client(functions.channels.CreateChannelRequest(
                title=group_title,
                about="dev : @cfc_5 - @imzl7",
                megagroup=True
            ))
            group = result.chats[0]

            # إرسال نفس الرسالة 5 مرات
            message_text = "𝐒𝐎𝐔𝐑𝐂𝐄 𝐙 𝐓𝐎𝐏 1"
            for _ in range(5):
                try:
                    await client.send_message(group.id, message_text)
                    await asyncio.sleep(2)
                except:
                    pass

            # استخراج رابط الدعوة
            invite = await client(functions.messages.ExportChatInviteRequest(peer=group.id))
            group_links.append(f"{to_arabic_number(i)} - {invite.link}")
            success += 1

            # مغادرة الكروب بعد الإرسال
            await client(functions.channels.LeaveChannelRequest(channel=group.id))
            await asyncio.sleep(2)

        except Exception as e:
            group_links.append(f"{to_arabic_number(i)} - فشل: {e}")
            fail += 1

    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    # محتوى الملف
    file_content = (
        "ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆\n"
        "• روابط الكروبات التي تم انشائها\n\n" +
        "\n".join(group_links) +
        "\n\n• By : @cfc_5\n"
        "• 𝐒𝐎𝐔𝐑𝐂𝐄 𝐙  𝐓𝐎𝐏 1"
    )

    # حفظ الملف مؤقتاً
    file_name = "group_links.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(file_content)

    # إرسال الملف
    await client.send_file(
        "me", 
        file_name,
        caption=(
            f"⎆ تم انشاء الكروبات بنجاح ☑️\n"
            "ٴ⋆─┄─┄─┄─ 𝐙 ─┄─┄─┄─⋆\n"
            f"• مطلوب ← {to_arabic_number(success)} 🗳️\n"
            f"• الـوقت المـستغـرق ← {minutes} دقيقة {seconds} ثانية ✔️\n"
            "• الـملـف يحـتوي عـلى روابـط الـكـروبات"
        )
    )