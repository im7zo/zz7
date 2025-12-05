import io
import sys
import traceback
from telethon import events
from config import client  # استيراد الكلاينت من ملف محفوظ

plugin_category = "الادوات"

@client.on(events.NewMessage(pattern=r"\.احسب (.+)"))
async def calculator(event):
    "لـ حل المعـادلات والمسائـل الرياضيـه"
    cmd = event.pattern_match.group(1)

    # استبدال الرموز الرياضية برموز بايثون
    cmd = cmd.replace("×", "*").replace("÷", "/").replace("^", "**")

    await event.edit("**⎉╎جـارِ الحـل .. انتظـر**")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    san = f"print({cmd})"
    try:
        await aexec(san, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "اسف لايمكنني حلها"
    final_output = "**📟╎المعـادلـة ⇜** `{}` \n\n**💡╎الحـل ⇜** `{}` \n".format(
        cmd, evaluation.strip()
    )
    await event.edit(final_output)

async def aexec(code, event):
    exec("async def __aexec(event): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](event)