import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ============================================================
# CONFIGURATION
# ============================================================

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))

# Discord Webhooks
# Discord Server 1
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Discord Server 2
DISCORD_WEBHOOK_URL_2 = os.getenv("DISCORD_WEBHOOK_URL_2")


# ============================================================
# HANDLE TELEGRAM CHANNEL POSTS
# ============================================================

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Make sure this is a channel post
    if not update.channel_post:
        return

    # Show which Telegram channel sent the message
    print(
        f"New post detected in channel: "
        f"{update.channel_post.chat_id}"
    )

    # Only process messages from the configured Telegram channel
    if update.channel_post.chat_id != TELEGRAM_CHANNEL_ID:
        return

    post = update.channel_post

    # Get caption or text
    caption = (
        post.caption
        if post.caption
        else (post.text if post.text else "")
    )

    file_to_send = None
    file_name = "file"

    # ========================================================
    # IDENTIFY MEDIA TYPE
    # ========================================================

    if post.photo:
        # Get the highest resolution photo
        file_to_send = await post.photo[-1].get_file()
        file_name = "image.jpg"

    elif post.video:
        # Get the video
        file_to_send = await post.video.get_file()
        file_name = "video.mp4"

    # ========================================================
    # SEND PHOTO / VIDEO
    # ========================================================

    if file_to_send:

        # Download file to temporary storage
        file_path = await file_to_send.download_to_drive()

        # ----------------------------------------------------
        # SEND TO DISCORD SERVER 1
        # ----------------------------------------------------

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

            print(
                f"Discord Server 1 status: "
                f"{response.status_code}"
            )

            if response.status_code >= 400:
                print(
                    f"Discord Server 1 error: "
                    f"{response.text}"
                )

        except Exception as e:
            print(f"Error sending to Discord Server 1: {e}")

        # ----------------------------------------------------
        # SEND TO DISCORD SERVER 2
        # ----------------------------------------------------

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

            print(
                f"Discord Server 2 status: "
                f"{response.status_code}"
            )

            if response.status_code >= 400:
                print(
                    f"Discord Server 2 error: "
                    f"{response.text}"
                )

        except Exception as e:
            print(f"Error sending to Discord Server 2: {e}")

        # Remove temporary file
        os.remove(file_path)

    # ========================================================
    # SEND TEXT-ONLY MESSAGE
    # ========================================================

    else:

        payload = {
            "content": caption
        }

        # ----------------------------------------------------
        # SEND TO DISCORD SERVER 1
        # ----------------------------------------------------

        try:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload
            )

            print(
                f"Discord Server 1 status: "
                f"{response.status_code}"
            )

            if response.status_code >= 400:
                print(
                    f"Discord Server 1 error: "
                    f"{response.text}"
                )

        except Exception as e:
            print(f"Error sending to Discord Server 1: {e}")

        # ----------------------------------------------------
        # SEND TO DISCORD SERVER 2
        # ----------------------------------------------------

        try:
            response = requests.post(
                DISCORD_WEBHOOK_URL_2,
                json=payload
            )

            print(
                f"Discord Server 2 status: "
                f"{response.status_code}"
            )

            if response.status_code >= 400:
                print(
                    f"Discord Server 2 error: "
                    f"{response.text}"
                )

        except Exception as e:
            print(f"Error sending to Discord Server 2: {e}")


# ============================================================
# START BOT
# ============================================================

if __name__ == "__main__":

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Listen for:
    # - Text
    # - Photos
    # - Videos

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
