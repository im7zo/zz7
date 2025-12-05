from telethon import events 
from config import client # استيراد client من ملف config

@client .on (events .NewMessage (outgoing =True ,pattern =r'\.عكس'))
async def rev (event ):
    if event .is_reply :
        replied =await event .get_reply_message ()
        reversed_text =replied .message [::-1 ]
        await client .edit_message (event .message ,reversed_text )