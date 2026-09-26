import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telethon import TelegramClient, events
from telethon.sessions import StringSession


# =========================
# ENVIRONMENT VARIABLES
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
PORT = int(os.getenv("PORT", "10000"))


# =========================
# AUTO REPLY
# =========================

BALASAN = [
    "RENTOD nya lagi sibuk!!!",
    "sabar ya cok,gua lagi ga on tele",
    "ciee ngechat,sange ya lu!!!",
    "pesan lu ntar gua bales kalo ga sibuk!!!",
    "lu ga penting,ntar aja chat nya gua bales"
]


# =========================
# TELEGRAM CLIENT
# =========================

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):

    # Hanya membalas chat pribadi
    if not event.is_private:
        return

    # Pilih balasan secara acak
    balasan = random.choice(BALASAN)

    await event.reply(balasan)


# =========================
# RENDER HTTP SERVER
# =========================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"Telegram Auto Reply aktif"
        )

    def log_message(self, format, *args):
        return


def run_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        Handler
    )
    server.serve_forever()


threading.Thread(
    target=run_server,
    daemon=True
).start()


# =========================
# START
# =========================

print("🤖 Telegram Auto-reply aktif di Render...")

client.start()
client.run_until_disconnected()
