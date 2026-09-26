import os
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

BALASAN = "Maaf, saat ini saya belum bisa membalas. Nanti saya hubungi kembali 🙏"

client = TelegramClient("userbot", API_ID, API_HASH)


@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if not event.is_private:
        return

    await event.reply(BALASAN)


print("🤖 Auto-reply Telegram aktif")

client.start()
client.run_until_disconnected()
