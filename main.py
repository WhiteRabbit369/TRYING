import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Config from Environment Variables

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))

# Discord Webhooks

DISCORD_WEBHOOK_URL_1 = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_WEBHOOK_URL_2 = os.getenv("DISCORD_WEBHOOK_URL_2")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
# Make sure this is a channel post
if not update.channel_post:
    return

# Show which Telegram channel sent the message
print(f"New post detected in channel: {update.channel_post.chat_id}")

# Only process messages from the configured Telegram channel
if update.channel_post.chat_id != TELEGRAM_CHANNEL_ID:
    return

post = update.channel_post

# Get caption or text
caption = post.caption if post.caption else (post.text if post.text else "")

file_to_send = None
file_name = "file"

# Identify media type
if post.photo:
    # Get the highest resolution photo
    file_to_send = await post.photo[-1].get_file()
    file_name = "image.jpg"

elif post.video:
    # Get the video
    file_to_send = await post.video.get_file()
    file_name = "video.mp4"

# Send photo or video
if file_to_send:

    # Download file
    file_path = await file_to_send.download_to_drive()

    # Send to Discord Server 1
    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (file_name, f)
            }

            payload = {
                "content": caption
            }

            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data=payload,
                files=files
            )

        print(f"Discord Server 1 status: {response.status_code}")

        if response.status_code >= 400:
            print(f"Discord Server 1 error: {response.text}")

    except Exception as e:
        print(f"Error sending to Discord Server 1: {e}")

    # Send to Discord Server 2
    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (file_name, f)
            }

            payload = {
                "content": caption
            }

            response = requests.post(
                DISCORD_WEBHOOK_URL_2,
                data=payload,
                files=files
            )

        print(f"Discord Server 2 status: {response.status_code}")

        if response.status_code >= 400:
            print(f"Discord Server 2 error: {response.text}")

    except Exception as e:
        print(f"Error sending to Discord Server 2: {e}")

    # Delete temporary file
    os.remove(file_path)

# Send text-only message
else:

    payload = {
        "content": caption
    }

    # Send to Discord Server 1
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_1,
            json=payload
        )

        print(f"Discord Server 1 status: {response.status_code}")

        if response.status_code >= 400:
            print(f"Discord Server 1 error: {response.text}")

    except Exception as e:
        print(f"Error sending to Discord Server 1: {e}")

    # Send to Discord Server 2
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL_2,
            json=payload
        )

        print(f"Discord Server 2 status: {response.status_code}")

        if response.status_code >= 400:
            print(f"Discord Server 2 error: {response.text}")

    except Exception as e:
        print(f"Error sending to Discord Server 2: {e}")
```

if **name** == "**main**":

```
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Listen for text, photos, and videos
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
print("Forwarding messages to Discord Server 1 and Server 2...")

app.run_polling()
```
