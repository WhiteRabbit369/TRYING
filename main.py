import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Config from Environment Variables
# Configuration (We will set these in Railway environment variables later)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))
DISCORD_WEBHOOK_URL_1 = os.getenv("DISCORD_WEBHOOK_URL_1")
DISCORD_WEBHOOK_URL_2 = os.getenv("DISCORD_WEBHOOK_URL_2")
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure the post is from the correct channel
    # Add this line right at the start of the function:
    print(f"New post detected in channel: {update.channel_post.chat_id}")
    
    if not update.channel_post or update.channel_post.chat_id != TELEGRAM_CHANNEL_ID:
        return

    post = update.channel_post
    caption = post.caption if post.caption else (post.text if post.text else "")

    file_to_send = None
    file_name = "file"

    # Identify Media Type
    if post.photo:
        # Get the highest resolution photo
        file_to_send = await post.photo[-1].get_file()
        file_name = "image.jpg"
    elif post.video:
        file_to_send = await post.video.get_file()
        file_name = "video.mp4"

    if file_to_send:
        # Download file to memory/temporary storage
        file_path = await file_to_send.download_to_drive()

        # Send to Discord as a file
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            payload = {"content": caption}
            response1 = requests.post(DISCORD_WEBHOOK_URL_1, data=payload, files=files)

        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            payload = {"content": caption}
            response1 = requests.post(DISCORD_WEBHOOK_URL_2, data=payload, files=files)

        # Clean up: Remove the downloaded file after sending
        os.remove(file_path)
    else:
        # Just text
        payload = {"content": caption}
        response1 = requests.post(DISCORD_WEBHOOK_URL_1, json=payload)
        response2 = requests.post(DISCORD_WEBHOOK_URL_2, json=payload)

    print(f"Status: {response.status_code}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Listen for text, photos, and videos
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & (filters.TEXT | filters.PHOTO | filters.VIDEO), handle_channel_post))

    print("Bot is monitoring media and text...")
    app.run_polling()
