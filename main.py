import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))

DISCORD_WEBHOOK_URL_1 = os.getenv("DISCORD_WEBHOOK_URL_1")
DISCORD_WEBHOOK_URL_2 = os.getenv("DISCORD_WEBHOOK_URL_2")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.channel_post:
    return

post = update.channel_post

print("New Telegram post detected:", post.chat_id)

if post.chat_id != TELEGRAM_CHANNEL_ID:
    return

caption = post.caption or post.text or ""

file_to_send = None
file_name = "file"

if post.photo:
    file_to_send = await post.photo[-1].get_file()
    file_name = "image.jpg"

if post.video:
    file_to_send = await post.video.get_file()
    file_name = "video.mp4"

if file_to_send:

    file_path = await file_to_send.download_to_drive()

    try:
        with open(file_path, "rb") as f:
            requests.post(
                DISCORD_WEBHOOK_URL_1,
                data={"content": caption},
                files={"file": (file_name, f)}
            )
        print("Sent media to Discord Server 1")
    except Exception as e:
        print("Server 1 error:", e)

    try:
        with open(file_path, "rb") as f:
            requests.post(
                DISCORD_WEBHOOK_URL_2,
                data={"content": caption},
                files={"file": (file_name, f)}
            )
        print("Sent media to Discord Server 2")
    except Exception as e:
        print("Server 2 error:", e)

    os.remove(file_path)

else:

    try:
        requests.post(
            DISCORD_WEBHOOK_URL_1,
            json={"content": caption}
        )
        print("Sent text to Discord Server 1")
    except Exception as e:
        print("Server 1 error:", e)

    try:
        requests.post(
            DISCORD_WEBHOOK_URL_2,
            json={"content": caption}
        )
        print("Sent text to Discord Server 2")
    except Exception as e:
        print("Server 2 error:", e)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(
MessageHandler(
filters.ChatType.CHANNEL
& (filters.TEXT | filters.PHOTO | filters.VIDEO),
handle_channel_post
)
)

print("Bot is running...")
print("Forwarding to two Discord servers...")

app.run_polling()
