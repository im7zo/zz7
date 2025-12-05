from telethon import events 
from config import client 

@client .on (events .NewMessage (outgoing =True ,pattern =r"^\.فاك$"))
async def fuck (event ):
    await event .edit (
    "┏━┳┳┳━┳┳┓\n"
    "┃━┫┃┃┏┫━┫┏┓\n"
    "┃┏┫┃┃┗┫┃┃┃┃\n"
    "┗┛┗━┻━┻┻┛┃┃\n"
    "┏┳┳━┳┳┳┓┏┫┣┳┓\n"
    "┣┓┃┃┃┃┣┫┃┏┻┻┫\n"
    "┃┃┃┃┃┃┃┃┣┻┫┃┃\n"
    "┗━┻━┻━┻┛┗━━━┛"
    )