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
    "𝙍𝙀𝙉𝙏𝙊𝘿 𝙣𝙮𝙖 𝙡𝙖𝙜𝙞 𝙨𝙞𝙗𝙪𝙠!!!",
    "𝙨𝙖𝙗𝙖𝙧 𝙮𝙖 𝙘𝙤𝙠,𝙜𝙪𝙖 𝙡𝙖𝙜𝙞 𝙜𝙖 𝙤𝙣 𝙩𝙚𝙡𝙚",
    "𝙘𝙞𝙚𝙚 𝙣𝙜𝙚𝙘𝙝𝙖𝙩,𝙨𝙖𝙣𝙜𝙚 𝙮𝙖 𝙡𝙪!!!",
    "𝙥𝙚𝙨𝙖𝙣 𝙡𝙪 𝙣𝙩𝙖𝙧 𝙜𝙪𝙖 𝙗𝙖𝙡𝙚𝙨 𝙠𝙖𝙡𝙤 𝙜𝙖 𝙨𝙞𝙗𝙪𝙠!!!",
    "𝙡𝙪 𝙜𝙖 𝙥𝙚𝙣𝙩𝙞𝙣𝙜,𝙣𝙩𝙖𝙧 𝙖𝙟𝙖 𝙘𝙝𝙖𝙩 𝙣𝙮𝙖 𝙜𝙪𝙖 𝙗𝙖𝙡𝙚𝙨"
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
# PENYIMPANAN PESAN BALASAN
# =========================================================

REPLY_MAP = {}


# =========================================================
# CEK APAKAH CHAT SUDAH PERNAH DIBALAS
# =========================================================

async def sudah_pernah_dibalas(chat_id):

    try:
        # Cari pesan keluar terakhir dari akun userbot
        pesan_keluar = await client.get_messages(
            chat_id,
            limit=1,
            from_user="me"
        )

        if pesan_keluar:
            return True

        return False

    except Exception as e:

        print(
            f"❌ GAGAL CEK RIWAYAT CHAT | {e}"
        )

        # Kalau gagal mengecek, jangan membalas
        # agar tidak terjadi balasan berulang
        return True


# =========================================================
# AUTO REPLY PESAN PRIBADI
# =========================================================

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):

    try:

        # Hanya chat pribadi
        if not event.is_private:
            return

        # Jangan proses pesan kosong
        if not event.message:
            return

        # AKTIF khusus untuk pengecekan userbot
        if event.raw_text.strip().upper() == "AKTIF":
            return

        # =================================================
        # CEK APAKAH AKUN INI SUDAH PERNAH DIBALAS
        # =================================================

        if await sudah_pernah_dibalas(event.chat_id):

            print(
                f"⏭️ SUDAH PERNAH DIBALAS"
                f" | chat={event.chat_id}"
            )

            return

        # =================================================
        # PILIH BALASAN ACAK
        # =================================================

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
# TEST USERBOT
# PERINTAH: AKTIF
# =========================================================

@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^AKTIF$"
))
async def test_userbot(event):

    if not event.is_private:
        return

    await event.reply("✅ USERBOT AKTIF")

    print(
        f"🧪 TEST USERBOT BERHASIL"
        f" | chat={event.chat_id}"
    )


# =========================================================
# TEST USERBOT DARI AKUN SENDIRI
# Bisa mengetik AKTIF di Saved Messages
# =========================================================

@client.on(events.NewMessage(
    outgoing=True,
    pattern=r"^AKTIF$"
))
async def test_userbot_sendiri(event):

    if not event.is_private:
        return

    await event.reply("✅ USERBOT AKTIF")

    print(
        f"🧪 TEST USERBOT BERHASIL"
        f" | chat={event.chat_id}"
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

        for incoming_id, data in list(REPLY_MAP.items()):

            saved_chat_id = data["chat_id"]
            reply_id = data["reply_id"]

            # Pastikan chat sama
            if saved_chat_id != chat_id:
                continue

            # Pesan pemicu sudah dibaca
            if incoming_id <= max_id:

                try:

                    await client.delete_messages(
                        chat_id,
                        reply_id
                    )

                    print(
                        f"🗑️ BALASAN DIHAPUS"
                        f" | chat={chat_id}"
                        f" | reply={reply_id}"
                    )

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

print(
    "🤖 Telegram Auto Reply sedang dimulai..."
)


async def start_telegram():

    await client.connect()

    if not await client.is_user_authorized():

        print(
            "❌ SESSION TIDAK VALID / BELUM LOGIN"
        )

        return

    me = await client.get_me()

    print(
        f"✅ LOGIN BERHASIL | "
        f"ID={me.id} | "
        f"USERNAME=@{me.username}"
    )

    print(
        "✅ Telegram Auto Reply AKTIF"
    )

    # Menjaga userbot tetap hidup
    await client.disconnected


client.loop.run_until_complete(
    start_telegram()
)
