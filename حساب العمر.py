from telethon import events
from datetime import datetime, timedelta
from config import client

@client.on(events.NewMessage(outgoing=True, pattern=r"\.حساب العمر (\d{4}/\d{1,2}/\d{1,2})"))
async def calculate_age(event):
    # فقط الحساب للصادر مني
    if not event.out:
        return

    text = event.pattern_match.group(1)
    try:
        # حذف رسالة الأمر
        await event.delete()

        birth_date = datetime.strptime(text, "%Y/%m/%d")
        now = datetime.now()

        # حساب العمر
        years = now.year - birth_date.year
        months = now.month - birth_date.month
        days = now.day - birth_date.day

        if days < 0:
            months -= 1
            prev_month = now.month - 1 if now.month > 1 else 12
            prev_year = now.year if now.month > 1 else now.year - 1
            days_in_prev_month = (datetime(prev_year, prev_month + 1, 1) - timedelta(days=1)).day
            days += days_in_prev_month

        if months < 0:
            years -= 1
            months += 12

        # كم باقي على عيد الميلاد القادم
        next_birthday_year = now.year if (now.month, now.day) < (birth_date.month, birth_date.day) else now.year + 1
        next_birthday = datetime(next_birthday_year, birth_date.month, birth_date.day)
        days_until_birthday = (next_birthday - now).days

        # رسالة الرد
        msg = (
            "ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 - حـساب الـعـمر  .\n"
            "⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
            f"𝑍╎العمر : {years} سنة\n"
            f"𝑍╎الأشهر: {months} شهر\n"
            f"𝑍╎الأيام: {days} يوم\n"
            f"𝑍╎عيد ميلادك بعد : {days_until_birthday} يوم"
        )

        await event.respond(msg)

    except ValueError:
        await event.edit("❗يـجـب إدخـال التـاريخ بصـيغة صـحيحة مـثلا `2010/1/20`")