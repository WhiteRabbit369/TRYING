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

print(f"New post detected in channel: {update.channel_post.chat_id}")

if update.channel_post.chat_id != TELEGRAM_CHANNEL_ID:
    return

post = update.channel_post

caption = post.caption if post.caption else (post.text if post.text else "")

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

    # Discord Server 1
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL_1,
                data={"content": caption},
                files={"file": (file_name, f)}
            )

        print(f"Discord Server 1 status: {response.status_code}")

    except Exception as e:
        print(f"Discord Server 1 error: {e}")

    # Discord Server 2
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL_2,
                data={"content": caption},
                files={"file": (file_name, f)}
            )

        print(f"Discord Server 2 status: {response.status_code}")

    except Exception as e:
        print(f"Discord Server 2 error: {e}")

    os.remove(file_path)

else:
    # Text message

    # Discord Server 1
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_1,
            json={"content": caption}
        )

        print(f"Discord Server 1 status: {response.status_code}")

    except Exception as e:
        print(f"Discord Server 1 error: {e}")

    # Discord Server 2
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_2,
            json={"content": caption}
        )

        print(f"Discord Server 2 status: {response.status_code}")

    except Exception as e:
        print(f"Discord Server 2 error: {e}")

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

print("Bot is monitoring media and text...")
print("Forwarding to Discord Server 1 and Server 2...")

app.run_polling()
