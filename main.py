import os
import random
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

BALASAN = [
    "RENTOD nya lagi sibuk!!!",
    "sabar ya cok,gua lagi ga on tele",
    "ciee ngechat,sange ya lu!!!",
    "pesan lu ntar gua bales kalo ga sibuk!!!",
    "lu ga penting,ntar aja chat nya gua bales"
]

client = TelegramClient("userbot", API_ID, API_HASH)


@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if not event.is_private:
        return

    await event.reply(random.choice(BALASAN))


print("🤖 Auto-reply aktif...")
client.start()
client.run_until_disconnected()
