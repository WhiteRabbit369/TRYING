import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))
DISCORD_WEBHOOK_URL_1 = os.getenv("DISCORD_WEBHOOK_URL_1")
DISCORD_WEBHOOK_URL_2 = os.getenv("DISCORD_WEBHOOK_URL_2")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("New Telegram post detected")

    if not update.channel_post:
    return

if update.channel_post.chat_id != TELEGRAM_CHANNEL_ID:
    return

post = update.channel_post

if post.caption:
    caption = post.caption
elif post.text:
    caption = post.text
else:
    caption = ""

file_to_send = None
file_name = "file"

if post.photo:
    file_to_send = await post.photo[-1].get_file()
    file_name = "image.jpg"

elif post.video:
    file_to_send = await post.video.get_file()
    file_name = "video.mp4"

if file_to_send:
    file_path = await file_to_send.download_to_drive()

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL_1,
                data={"content": caption},
                files={"file": (file_name, f)}
            )

        print("Discord Server 1:", response.status_code)

    except Exception as e:
        print("Discord Server 1 error:", e)

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL_2,
                data={"content": caption},
                files={"file": (file_name, f)}
            )

        print("Discord Server 2:", response.status_code)

    except Exception as e:
        print("Discord Server 2 error:", e)

    os.remove(file_path)

else:
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_1,
            json={"content": caption}
        )

        print("Discord Server 1:", response.status_code)

    except Exception as e:
        print("Discord Server 1 error:", e)

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_2,
            json={"content": caption}
        )

        print("Discord Server 2:", response.status_code)

    except Exception as e:
        print("Discord Server 2 error:", e)

if **name** == "**main**":
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.ChatType.CHANNEL
        & (
            filters.TEXT
            | filters.PHOTO
            | filters.VIDEO
        ),
        handle_channel_post
    )
)

print("Bot is monitoring Telegram...")
print("Forwarding to Discord Server 1 and Server 2...")

app.run_polling()
