from telethon import events 
from config import client 
from Z .حب import Lovely # ✅ هذا أهم تعديل
import asyncio 

lovely =Lovely ()

@client .on (events .NewMessage (outgoing =True ,pattern =r"\.حب$"))
async def lovelyrun (event ):
    for d in lovely .lovely :
        await event .edit (d )
        await asyncio .sleep (0.3 )