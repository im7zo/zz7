from telethon import events
import yt_dlp
import os
import requests
from config import client  # تأكد إن client موجود بالسورس

@client.on(events.NewMessage(pattern=r"\.بحث (.+)"))
async def search_youtube(event):
    query = event.pattern_match.group(1)

    # تعديل رسالة المستخدم لتظهر التحميل
    msg = await event.edit("╮ جـارِ التحميل ▬▭ . . .🎧♥️╰")

    # إعدادات yt-dlp لتحويل الصوت إلى mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True
    }

    try:
        os.makedirs("downloads", exist_ok=True)

        # تحميل الصوت واستخراج معلومات الفيديو
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

            # تحميل صورة الغلاف
            thumb_url = info.get("thumbnail")
            thumb_file = "thumb.jpg"
            if thumb_url:
                r = requests.get(thumb_url)
                with open(thumb_file, "wb") as f:
                    f.write(r.content)
            else:
                thumb_file = None

        # حذف رسالة التحميل
        await msg.delete()

        # تنظيف العنوان من أي backticks حتى لا يكسر Markdown
        title = info['title'].replace('`', '')

        # إرسال الملف الصوتي مع العنوان القابل للنسخ
        await event.reply(
            file=filename,
            message=f"⎉ البحث ⥃ `{title}`",
            parse_mode="markdown",
            thumb=thumb_file
        )

        # حذف الملفات المؤقتة
        os.remove(filename)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)

    except Exception as e:
        await event.reply(f"فـشل فـي تحميل الـمحـتوى اعـد المحـاولة لاحـقا  {e}")