from telethon import events
from datetime import datetime, timedelta
from config import client

@client.on(events.NewMessage(outgoing=True, pattern=r"\.حساب العمر (\d{4}/\d{1,2}/\d{1,2})"))
async def calculate_age(event):
    date_text = event.pattern_match.group(1)

    try:
        # حذف رسالة الأمر
        await event.delete()

        birth_date = datetime.strptime(date_text, "%Y/%m/%d")
        now = datetime.now()

        # الحساب الأولي
        years = now.year - birth_date.year
        months = now.month - birth_date.month
        days = now.day - birth_date.day

        # تصحيح الأيام
        if days < 0:
            months -= 1
            last_month = now.replace(day=1) - timedelta(days=1)
            days += last_month.day

        # تصحيح الأشهر
        if months < 0:
            years -= 1
            months += 12

        # حساب المتبقي على عيد الميلاد القادم
        next_birthday = birth_date.replace(year=now.year)
        if next_birthday < now:
            next_birthday = next_birthday.replace(year=now.year + 1)

        days_until_birthday = (next_birthday - now).days

        msg = (
            "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 - حـساب الـعـمر .\n"
            "⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
            f"𝑍╎العمر : {years} سنة\n"
            f"𝑍╎الأشهر : {months} شهر\n"
            f"𝑍╎الأيام : {days} يوم\n"
            f"𝑍╎عيد ميلادك بعد : {days_until_birthday} يوم"
        )

        await client.send_message(event.chat_id, msg)

    except ValueError:
        await client.send_message(
            event.chat_id,
            "❗يجب إدخال التاريخ بصيغة صحيحة\nمثال: `2010/1/20`"
        )