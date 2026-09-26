import os
import random
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

from telethon import TelegramClient, events
from telethon.sessions import StringSession


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
PORT = int(os.getenv("PORT", "10000"))


# =========================================================
# AUTO REPLY
# =========================================================

BALASAN = [
    "RENTOD nya lagi sibuk!!!",
    "sabar ya cok,gua lagi ga on tele",
    "ciee ngechat,sange ya lu!!!",
    "pesan lu ntar gua bales kalo ga sibuk!!!",
    "lu ga penting,ntar aja chat nya gua bales"
]


# =========================================================
# TELEGRAM CLIENT
# =========================================================

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


# =========================================================
# PENYIMPANAN PESAN
# =========================================================

# Format:
#
# {
#     incoming_message_id: {
#         "chat_id": chat_id,
#         "reply_id": id_balasan
#     }
# }
#
REPLY_MAP = {}


# =========================================================
# AUTO REPLY PESAN PRIBADI
# =========================================================

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):

    try:

        # Hanya chat pribadi
        if not event.is_private:
            return

        # Jangan proses service message
        if not event.message:
            return

        # Pilih balasan acak
        balasan = random.choice(BALASAN)

        # Kirim balasan
        reply = await event.reply(balasan)

        # Simpan hubungan pesan masuk dan balasan
        REPLY_MAP[event.id] = {
            "chat_id": event.chat_id,
            "reply_id": reply.id
        }

        print(
            f"📩 PESAN MASUK"
            f" | chat={event.chat_id}"
            f" | pesan={event.id}"
        )

        print(
            f"💬 BALASAN"
            f" | pesan={reply.id}"
        )

    except Exception as e:

        print(
            f"❌ ERROR AUTO REPLY: {e}"
        )


# =========================================================
# HAPUS BALASAN KETIKA PESAN SUDAH DIBACA
# =========================================================

@client.on(events.MessageRead(inbox=True))
async def message_read(event):

    try:
        await asyncio.sleep(1)
        chat_id = event.chat_id
        max_id = event.max_id

        print(
            f"👀 PESAN DIBACA"
            f" | chat={chat_id}"
            f" | max_id={max_id}"
        )

        # Ambil salinan supaya dictionary
        # aman ketika sedang dihapus
        for incoming_id, data in list(REPLY_MAP.items()):

            saved_chat_id = data["chat_id"]
            reply_id = data["reply_id"]

            # Pastikan chat sama
            if saved_chat_id != chat_id:
                continue

            # Pesan pemicu sudah dibaca
            if incoming_id <= max_id:

                try:

                    # Hapus balasan otomatis
                    await client.delete_messages(
                        chat_id,
                        reply_id
                    )

                    print(
                        f"🗑️ BALASAN DIHAPUS"
                        f" | chat={chat_id}"
                        f" | reply={reply_id}"
                    )

                    # Hapus dari daftar
                    del REPLY_MAP[incoming_id]

                except Exception as e:

                    print(
                        f"❌ GAGAL HAPUS BALASAN"
                        f" | {e}"
                    )

    except Exception as e:

        print(
            f"❌ ERROR MESSAGE READ: {e}"
        )

# =========================================================
# TEST USERBOT
# =========================================================

@client.on(events.NewMessage(pattern=r"^/test$"))
async def test_userbot(event):

    if not event.is_private:
        return

    await event.reply("✅ USERBOT AKTIF")
    print("🧪 TEST USERBOT BERHASIL")
    @client.on(events.MessageRead())
async def message_read(event):
    try:
        await asyncio.sleep(1)

        chat_id = event.chat_id
        max_id = event.max_id

        print(
            f"👀 PESAN DIBACA | chat={chat_id} | max_id={max_id}"
        )

        for incoming_id, data in list(REPLY_MAP.items()):

            if data["chat_id"] != chat_id:
                continue

            if incoming_id <= max_id:

                try:
                    await client.delete_messages(
                        chat_id,
                        data["reply_id"]
                    )

                    print(
                        f"🗑️ BALASAN DIHAPUS | "
                        f"chat={chat_id} | "
                        f"reply={data['reply_id']}"
                    )

                    del REPLY_MAP[incoming_id]

                except Exception as e:
                    print(f"❌ GAGAL HAPUS BALASAN | {e}")

    except Exception as e:
        print(f"❌ ERROR MESSAGE READ: {e}")
# =========================================================
# RENDER WEB SERVER
# =========================================================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain"
        )
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

    print(
        f"🌐 Web server aktif di port {PORT}"
    )

    server.serve_forever()


# =========================================================
# START WEB SERVER
# =========================================================

threading.Thread(
    target=run_server,
    daemon=True
).start()


# =========================================================
# START TELEGRAM
# =========================================================

print("🤖 Telegram Auto Reply sedang dimulai...")

# =========================================================
# START TELEGRAM
# =========================================================

print("🤖 Telegram Auto Reply sedang dimulai...")


async def start_telegram():

    await client.connect()

    if not await client.is_user_authorized():
        print("❌ SESSION TIDAK VALID / BELUM LOGIN")
        return

    me = await client.get_me()

    print(
        f"✅ LOGIN BERHASIL | "
        f"ID={me.id} | "
        f"USERNAME=@{me.username}"
    )

    print("✅ Telegram Auto Reply AKTIF")

    # Menjaga userbot tetap hidup
    await client.disconnected


client.loop.run_until_complete(start_telegram())
