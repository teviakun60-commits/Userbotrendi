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


# Menyimpan pesan masuk dan
# balasan otomatisnya
REPLY_MAP = {}


# =========================
# AUTO REPLY
# =========================

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):

    # Hanya chat pribadi
    if not event.is_private:
        return

    balasan = random.choice(BALASAN)

    # Kirim balasan
    reply = await event.reply(balasan)

    # Simpan hubungan pesan
    REPLY_MAP[event.id] = {
        "chat_id": event.chat_id,
        "reply_id": reply.id
    }

    print(
        f"📩 Pesan masuk: {event.id} | "
        f"Balasan: {reply.id}"
    )


# =========================
# HAPUS BALASAN SAAT PESAN
# SUDAH DIBACA
# =========================

@client.on(events.MessageRead(incoming=True))
async def message_read(event):

    try:
        for message_id in event.message_ids:

            if message_id not in REPLY_MAP:
                continue

            data = REPLY_MAP[message_id]

            chat_id = data["chat_id"]
            reply_id = data["reply_id"]

            # Hapus balasan otomatis
            await client.delete_messages(
                chat_id,
                reply_id
            )

            print(
                f"🗑️ Balasan {reply_id} "
                f"dihapus karena pesan sudah dibaca"
            )

            # Hapus data dari memory
            del REPLY_MAP[message_id]

    except Exception as e:
        print("❌ Error menghapus balasan:", e)


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
