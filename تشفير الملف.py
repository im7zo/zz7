# أمر .تشفير الملف لتشفير ملفات Python (.py) باستخدام marshal + base64
from telethon import events
import os
import base64
import marshal
from config import client

@client.on(events.NewMessage(pattern=r"^\.تشفير الملف(?:\s+(\d+))?$"))
async def encrypt_handler(event):
    try:
        me = await client.get_me()
        if event.sender_id != me.id:
            return  # يعمل فقط إذا الرسالة منك

        reply = await event.get_reply_message()
        if not reply or not reply.file:
            await event.edit("""❗يـجـب الـرد علـى ملـف .py 
مثـال: `.تشفير الملف 3`""")
            return

        layers_arg = event.pattern_match.group(1)
        try:
            layers = int(layers_arg) if layers_arg else 1
        except:
            layers = 1
        if layers < 1:
            layers = 1
        if layers > 10:
            await event.edit("❗الـحد الأقـصى للطـبقات هـو 10")
            return

        fname = reply.file.name or 'file.py'
        if not fname.lower().endswith('.py'):
            await event.edit('❗يـجـب الـرد علـى ملـف **Python (.py)**')
            return

        tmp_dir = './.tmp_encrypt'
        os.makedirs(tmp_dir, exist_ok=True)
        in_path = os.path.join(tmp_dir, fname)
        await client.download_media(reply, in_path)

        with open(in_path, 'rb') as f:
            src_bytes = f.read()

        try:
            src_text = src_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                src_text = src_bytes.decode('latin-1')
            except:
                await event.edit('فـشل قـراءة المـلف: التـرميز غـير مـدعـوم')
                return

        current_source = src_text

        for i in range(layers):
            try:
                codeobj = compile(current_source, '<enc>', 'exec')
            except Exception as e:
                await event.edit(f'خـطأ أثـناء تجـميع الشيـفرة فـي الطبـقة {i+1}: {e}')
                return

            marsh = marshal.dumps(codeobj)
            b64 = base64.b64encode(marsh).decode('utf-8')
            current_source = (
                "import marshal,base64\n"
                "exec(marshal.loads(base64.b64decode('" + b64 + "')))\n"
            )

        # اسم الملف النهائي ثابت
        out_name = 'Z-userbot.py'
        out_path = os.path.join(tmp_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(current_source)

        await event.edit(f'تـم تشـفير المـلف بعـدد طبـقات: **{layers}** يـتم الارسـال')
        await event.respond(file=out_path)

        try:
            os.remove(in_path)
            os.remove(out_path)
        except:
            pass

    except Exception as e:
        await event.edit(f'حـدث خطـأ غـير متـوقع: {e}')