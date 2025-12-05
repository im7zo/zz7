from telethon import events 
from config import client 
import random 

gn =["""
🌙.     *       ☄️      
🌟   .  *       .         
                       *   .      🛰     .        ✨      *
  .     *   روح نام         🚀     
      .              . . احلام سعيدة 🌙
. *       🌏 بيباي         *
                     🌙.     *       ☄️      
🌟   .  *       .         
                       *   .      🛰     .        ✨      *
"""]

@client .on (events .NewMessage (outgoing =True ,pattern =r"\.نام$"))
async def goodnight (event ):
    ggn =random .choice (gn )
    await event .edit (ggn )